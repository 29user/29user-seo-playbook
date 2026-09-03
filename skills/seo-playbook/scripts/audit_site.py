#!/usr/bin/env python3
"""Crawl a live site and report the SEO defects that break silently.

Every check here exists because the defect it catches shipped to production on a
real site, looked fine in the browser, and was only visible in a third-party
audit weeks later. Standard library only, no API keys, no crawl budget.

    python3 audit_site.py https://example.com
    python3 audit_site.py https://example.com --limit 50 --json report.json

Exit code is 1 when any ERROR-level finding is present, so it can gate CI.
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import gzip
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit

UA = "Mozilla/5.0 (compatible; seo-playbook-audit/1.0; +https://github.com/29user/seo-playbook)"
TIMEOUT = 25

RESERVED_HOSTS = {
    "example.com", "example.net", "example.org", "example.edu",
    "localhost", "invalid", "test",
}

TITLE_MAX = 60
DESC_MIN, DESC_MAX = 110, 160

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', re.S | re.I)
CANON_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']', re.I)
ALT_RE = re.compile(
    r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\']([^"\']+)["\'][^>]+href=["\']([^"\']+)["\']',
    re.I,
)
ALT_RE_SWAPPED = re.compile(
    r'<link[^>]+hreflang=["\']([^"\']+)["\'][^>]+rel=["\']alternate["\'][^>]+href=["\']([^"\']+)["\']',
    re.I,
)
OG_IMAGE_RE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', re.I)
H1_RE = re.compile(r"<h1[^>]*>", re.I)
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)
SITEMAP_DIRECTIVE_RE = re.compile(r"^\s*sitemap:\s*(\S+)", re.I | re.M)

# Characters that carry no visible glyph and have no business in markup. They
# arrive with model-written copy and silently break length budgets, JSON-LD
# validation, slugs and in-page search.
INVISIBLE = {
    "​", "‌", "⁠", "﻿", "­", "᠎", "᠏",
    "ㅤ", "ﾠ", "⁥",
}
INVISIBLE |= {chr(c) for c in range(0x202A, 0x202F)}
INVISIBLE |= {chr(c) for c in range(0x2066, 0x206A)}
INVISIBLE |= {chr(c) for c in range(0xE0000, 0xE0080)}


@dataclass
class Finding:
    level: str  # ERROR | WARN | INFO
    check: str
    url: str
    detail: str


@dataclass
class Page:
    url: str
    status: int = 0
    seconds: float = 0.0
    html: str = ""
    error: str = ""
    location: str = ""
    final_url: str = ""

    @property
    def redirected(self) -> bool:
        return bool(self.final_url) and self.final_url.rstrip("/") != self.url.rstrip("/")

    @property
    def head(self) -> str:
        return self.html.split("</head>", 1)[0] if self.html else ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    pages_checked: int = 0
    notes: list[str] = field(default_factory=list)

    def add(self, level: str, check: str, url: str, detail: str) -> None:
        self.findings.append(Finding(level, check, url, detail))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


def fetch(url: str, method: str = "GET", follow: bool = True) -> Page:
    import time

    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    started = time.monotonic()
    opener = urllib.request.urlopen
    if not follow:
        opener = urllib.request.build_opener(_NoRedirect).open
    try:
        with opener(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            charset = resp.headers.get_content_charset() or "utf-8"
            return Page(
                url=url,
                status=resp.status,
                seconds=time.monotonic() - started,
                html=raw.decode(charset, "replace"),
                final_url=resp.url,
            )
    except urllib.error.HTTPError as exc:
        # With follow=False a 3xx arrives here; keep the Location for the caller.
        return Page(
            url=url,
            status=exc.code,
            seconds=time.monotonic() - started,
            location=exc.headers.get("Location", ""),
        )
    except Exception as exc:  # noqa: BLE001 - network reality, report and continue
        return Page(url=url, error=f"{type(exc).__name__}: {exc}", seconds=time.monotonic() - started)


def unescape(text: str) -> str:
    import html as html_mod

    return html_mod.unescape(text).strip()


def first(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text)
    return unescape(m.group(1)) if m else None


def alternates(head: str) -> dict[str, str]:
    """{hreflang: absolute url}. Attribute order varies between templates."""
    found = ALT_RE.findall(head) + [(lang, href) for lang, href in ALT_RE_SWAPPED.findall(head)]
    return {lang.lower(): unescape(href) for lang, href in found}


def invisible_hits(text: str) -> list[str]:
    hits = []
    for i, ch in enumerate(text):
        if ch in INVISIBLE or (unicodedata.category(ch) == "Cf" and ch != "‍"):
            hits.append(f"U+{ord(ch):04X}@{i}")
    return hits


def discover_urls(site: str, limit: int, report: Report,
                  explicit_sitemap: str | None = None) -> list[str]:
    """Sitemap first (it is the site's own claim about what should be indexed)."""
    root = f"{urlsplit(site).scheme}://{urlsplit(site).netloc}"
    candidates: list[str] = [explicit_sitemap] if explicit_sitemap else []

    robots = fetch(urljoin(root, "/robots.txt"))
    if robots.status == 200:
        candidates += SITEMAP_DIRECTIVE_RE.findall(robots.html)
    else:
        report.add("ERROR", "robots", urljoin(root, "/robots.txt"),
                   f"robots.txt returned {robots.status or robots.error} on GET")
    candidates.append(urljoin(root, "/sitemap.xml"))

    urls: list[str] = []
    seen_maps: set[str] = set()
    queue = list(dict.fromkeys(candidates))
    while queue and len(urls) < limit:
        sm_url = queue.pop(0)
        if sm_url in seen_maps:
            continue
        seen_maps.add(sm_url)
        sm = fetch(sm_url)
        if sm.status != 200:
            if sm_url.endswith("/sitemap.xml") and not urls:
                report.add("ERROR", "sitemap", sm_url,
                           f"sitemap returned {sm.status or sm.error} on GET")
            continue
        locs = LOC_RE.findall(sm.html)
        if "<sitemapindex" in sm.html.lower():
            queue.extend(locs)  # index of sitemaps, not of pages
            continue
        urls.extend(locs)

    if not urls:
        report.notes.append(
            "NO SITEMAP FOUND — the crawl started from the entry URL alone. "
            "Coverage-dependent checks (duplicate title/description, og:image "
            "across the site) saw only what was reached. Pass --sitemap <url> for "
            "a real site audit."
        )
        urls = [site]
    return list(dict.fromkeys(urls))[:limit]


def check_page(page: Page, report: Report) -> None:
    if page.error or page.status != 200:
        report.add("ERROR", "status", page.url, f"{page.status or page.error}")
        return

    head = page.head

    title = first(TITLE_RE, head)
    if not title:
        report.add("ERROR", "title", page.url, "missing <title>")
    elif len(title) > TITLE_MAX:
        report.add("WARN", "title", page.url,
                   f"{len(title)} chars (>{TITLE_MAX}) — Google will rewrite it")

    desc = first(DESC_RE, head)
    if desc is None:
        report.add("ERROR", "description", page.url, "missing meta description")
    elif not (DESC_MIN <= len(desc) <= DESC_MAX):
        report.add("WARN", "description", page.url,
                   f"{len(desc)} chars, want {DESC_MIN}-{DESC_MAX}")

    canonical = first(CANON_RE, head)
    if not canonical:
        report.add("WARN", "canonical", page.url, "missing canonical")
    elif not canonical.startswith(("http://", "https://")):
        report.add("WARN", "canonical", page.url, f"not absolute: {canonical}")

    hits = invisible_hits(head)
    if hits:
        report.add("ERROR", "invisible-chars", page.url,
                   f"{len(hits)} invisible char(s) in <head>: {', '.join(hits[:5])}")

    h1s = len(H1_RE.findall(page.html))
    if h1s == 0:
        report.add("WARN", "h1", page.url, "no <h1>")
    elif h1s > 1:
        report.add("INFO", "h1", page.url, f"{h1s} <h1> tags")

    if page.seconds > 2.0:
        report.add("WARN", "speed", page.url, f"{page.seconds:.1f}s to fetch")


def fetch_missing_alternates(pages: dict[str, Page], report: Report, cap: int = 60) -> None:
    """Pull in hreflang targets that fell outside the crawl slice.

    Reciprocity cannot be judged from one side, and with --limit the counterpart
    is often just below the cutoff — warning about it would blame correct markup.
    """
    wanted: set[str] = set()
    for page in list(pages.values()):
        if page.status != 200:
            continue
        for lang, target in alternates(page.head).items():
            if lang != "x-default" and target not in pages:
                wanted.add(target)
    if not wanted:
        return
    extra = sorted(wanted)[:cap]
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        for fetched in pool.map(fetch, extra):
            pages[fetched.url] = fetched
    report.notes.append(f"fetched {len(extra)} hreflang counterpart(s) outside the crawl slice")


def check_hreflang(pages: dict[str, Page], report: Report) -> None:
    """The defect that is invisible in a browser and costs the most.

    A language group must be closed: every page it names must name it back, and
    x-default must point at the default-language version OF THAT PAGE, not at
    the site home. One hardcoded x-default breaks every page at once.
    """
    groups = {url: alternates(p.head) for url, p in pages.items() if p.status == 200}
    default_lang_hint = None
    for alts in groups.values():
        for lang in alts:
            if lang != "x-default":
                default_lang_hint = default_lang_hint or lang
        break

    unverifiable: list[str] = []
    missing_self: list[str] = []
    one_way: dict[str, list[str]] = {}
    for url, alts in groups.items():
        if not alts:
            continue
        canonical = first(CANON_RE, pages[url].head) or url

        xdefault = alts.get("x-default")
        if xdefault:
            # The default version of this page is whichever alternate is not the
            # current language; with a single alternate it is the page itself.
            same_page_alternates = {v for k, v in alts.items() if k != "x-default"}
            xd_page = pages.get(xdefault)
            if xd_page is not None and xd_page.redirected:
                same_page_alternates.add(xdefault)  # judged by the redirect check
            if xdefault not in same_page_alternates and xdefault != canonical:
                report.add("ERROR", "hreflang-x-default", url,
                           f"x-default={xdefault} is not an alternate of this page "
                           f"(likely hardcoded to the site home)")

        for lang, target in alts.items():
            if lang == "x-default" or target == canonical:
                continue
            target_page = pages.get(target)
            if target_page is not None and target_page.redirected:
                # A redirecting alternate is a real finding, but it is not a
                # broken group: the markup at the destination belongs to another
                # URL and cannot be judged as this one's return tag.
                report.add("WARN", "hreflang-redirect", url,
                           f"{lang}={target} redirects to {target_page.final_url} — "
                           f"point hreflang at the final URL")
                continue
            other = groups.get(target)
            if other is None:
                unverifiable.append(f"{url} -> {target}")
                continue

            # Real schemes vary. Some sites omit the self-referencing tag, and
            # some represent the default locale only as x-default. Neither is a
            # broken group, so only a target that never names this page at all
            # is an error.
            if other.get(lang) != target:
                missing_self.append(target)

            names_us = {v.rstrip("/") for v in other.values()}
            us = {canonical.rstrip("/"), url.rstrip("/")}
            if pages[url].final_url:
                us.add(pages[url].final_url.rstrip("/"))
            if not (names_us & us):
                one_way.setdefault(url, []).append(target)

    for url, targets in one_way.items():
        declared = len([k for k in groups[url] if k != "x-default"])
        if declared and len(targets) >= max(2, declared - 1):
            # Every counterpart ignores this URL: the page itself is outside its
            # own language group. One cause, so one finding.
            report.add("ERROR", "hreflang-orphan", url,
                       f"declares {declared} alternates and none of them link back — "
                       f"this URL is not part of the group it points into "
                       f"(often a locale-less root that the localized pages ignore)")
        else:
            shown = ", ".join(targets[:3])
            more = f" (+{len(targets) - 3} more)" if len(targets) > 3 else ""
            report.add("ERROR", "hreflang-return", url,
                       f"points to {shown}{more}, which do not link back")

    if missing_self:
        # Google asks each version to list itself. Plenty of large sites skip it
        # and still work, so this is a recommendation, not a break — and it is
        # aggregated because it is per-locale and would otherwise flood.
        uniq = sorted(set(missing_self))
        report.add("WARN", "hreflang-self", uniq[0],
                   f"{len(uniq)} page(s) do not declare a self-referencing hreflang "
                   f"(Google asks every version to list itself)")

    if unverifiable:
        # One aggregated line: on a site with many locales this would otherwise
        # bury the real findings under hundreds of identical warnings.
        report.add("INFO", "hreflang-coverage", unverifiable[0].split(" -> ")[0],
                   f"{len(unverifiable)} alternate(s) outside the crawl — "
                   f"raise --limit to verify their return tags")


def check_duplicates(pages: dict[str, Page], report: Report) -> None:
    titles: dict[str, list[str]] = {}
    descs: dict[str, list[str]] = {}
    for url, page in pages.items():
        if page.status != 200:
            continue
        t = first(TITLE_RE, page.head)
        d = first(DESC_RE, page.head)
        if t:
            titles.setdefault(t, []).append(url)
        if d:
            descs.setdefault(d, []).append(url)
    for value, urls in titles.items():
        if len(urls) > 1:
            report.add("WARN", "duplicate-title", urls[0],
                       f"{len(urls)} pages share the title {value[:50]!r}")
    for value, urls in descs.items():
        if len(urls) > 1:
            report.add("WARN", "duplicate-description", urls[0],
                       f"{len(urls)} pages share one description")


def check_host_variants(site: str, report: Report) -> None:
    """www that resolves but is not served drops the connection entirely.

    An audit reads that as "robots.txt is not accessible" and the real cause —
    a missing certificate or host binding — is nowhere in the message.
    """
    parts = urlsplit(site)
    host = parts.netloc
    bare = host[4:] if host.startswith("www.") else host
    www = host if host.startswith("www.") else f"www.{host}"

    for variant in (bare, www):
        probe = fetch(f"https://{variant}/", follow=False)
        if probe.error:
            report.add("ERROR", "host", f"https://{variant}/",
                       f"does not serve: {probe.error} (DNS may resolve while the "
                       f"host is unbound or has no certificate)")
        elif variant == www and probe.status == 200:
            canonical_host = ""
            served = fetch(f"https://{variant}/")
            canonical = first(CANON_RE, served.head) if served.html else None
            if canonical:
                canonical_host = urlsplit(canonical).netloc.lower()
            if canonical_host and canonical_host != variant:
                report.add("INFO", "host", f"https://{variant}/",
                           f"serves 200 but canonicalises to {canonical_host} — "
                           f"a 301 would be cheaper than relying on canonical")
            else:
                report.add("WARN", "host", f"https://{variant}/",
                           "both hosts serve content — pick one and 301 the other, "
                           "or they compete as duplicates")


def check_orphans(pages: dict[str, Page], report: Report) -> None:
    """Pages nothing links to.

    A URL can sit in the sitemap, return 200 and still be invisible: crawlers
    reach pages by following links, and a page with no incoming internal link
    has no path to it and no share of the site's authority. This is a frequent
    reason a freshly published page never gets indexed.
    """
    linked: set[str] = set()
    for page in pages.values():
        if page.status != 200:
            continue
        base = page.final_url or page.url
        for href in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']', page.html, re.I):
            if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue
            target = urljoin(base, href).split("#")[0]
            linked.add(target.rstrip("/"))

    orphans = [
        url for url, page in pages.items()
        if page.status == 200 and url.rstrip("/") not in linked
        and (page.final_url or url).rstrip("/") not in linked
    ]
    # The entry URL is normally reached directly, not by an internal link.
    orphans = [u for u in orphans if urlsplit(u).path not in ("", "/")]
    for url in orphans[:20]:
        report.add("WARN", "orphan-page", url,
                   "no internal links point here — crawlers arrive only via the "
                   "sitemap, and the page gets no internal authority")
    if len(orphans) > 20:
        report.add("INFO", "orphan-page", orphans[0],
                   f"{len(orphans)} orphan pages in total")


def check_og_image(pages: dict[str, Page], report: Report) -> None:
    """One broken share image is usually referenced site-wide, and often also
    sits inside JSON-LD, where it fails structured-data validation."""
    images = {
        first(OG_IMAGE_RE, p.head)
        for p in pages.values()
        if p.status == 200 and first(OG_IMAGE_RE, p.head)
    }
    for image in list(images)[:5]:
        probe = fetch(image)
        if probe.status != 200:
            report.add("ERROR", "og-image", image,
                       f"og:image returns {probe.status or probe.error}")


def render(report: Report, site: str) -> str:
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings = sorted(report.findings, key=lambda f: (order[f.level], f.check, f.url))
    errors = sum(1 for f in findings if f.level == "ERROR")
    warns = sum(1 for f in findings if f.level == "WARN")

    lines = [
        f"SEO audit — {site}",
        f"pages checked: {report.pages_checked} | errors: {errors} | warnings: {warns}",
        "",
    ]
    lines += [f"note: {n}" for n in report.notes]
    if report.notes:
        lines.append("")

    if not findings:
        lines.append("No findings. Checked: status, title, description, canonical,")
        lines.append("hreflang groups, x-default, invisible characters, h1, duplicates,")
        lines.append("og:image, robots/sitemap over GET, www vs bare host.")
        return "\n".join(lines)

    PER_CHECK = 8
    current = None
    shown = 0
    for f in findings:
        if f.check != current:
            current = f.check
            shown = 0
            total = sum(1 for x in findings if x.check == f.check)
            suffix = f" ({total} findings)" if total > PER_CHECK else ""
            lines.append(f"[{f.level}] {f.check}{suffix}")
        shown += 1
        if shown == PER_CHECK + 1:
            total = sum(1 for x in findings if x.check == f.check)
            lines.append(f"  ... and {total - PER_CHECK} more — use --json for the full list")
        if shown > PER_CHECK:
            continue
        lines.append(f"  {f.url}")
        lines.append(f"    {f.detail}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a live site for silent SEO defects.")
    parser.add_argument("site", help="site URL, e.g. https://example.com")
    parser.add_argument("--limit", type=int, default=200, help="max pages to fetch (default 200)")
    parser.add_argument("--workers", type=int, default=8, help="parallel fetches (default 8)")
    parser.add_argument("--sitemap", metavar="URL", help="explicit sitemap URL if discovery fails")
    parser.add_argument("--json", metavar="PATH", help="also write findings as JSON")
    args = parser.parse_args()

    site = args.site if args.site.startswith("http") else f"https://{args.site}"

    host = urlsplit(site).netloc.lower().removeprefix("www.")
    if host in RESERVED_HOSTS or host.endswith(".invalid") or host.endswith(".test"):
        print(
            f"{host} is a reserved documentation domain (RFC 2606), not a real site.\n"
            f"Findings from it would describe IANA's placeholder page. "
            f"Pass the actual hostname."
        )
        return 2

    report = Report()

    urls = discover_urls(site, args.limit, report, explicit_sitemap=args.sitemap)
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pages = {p.url: p for p in pool.map(fetch, urls)}
    report.pages_checked = len(pages)

    fetch_missing_alternates(pages, report)
    report.pages_checked = len(pages)

    for page in pages.values():
        check_page(page, report)
    check_hreflang(pages, report)
    check_duplicates(pages, report)
    check_og_image(pages, report)
    check_orphans(pages, report)
    check_host_variants(site, report)

    print(render(report, site))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "site": site,
                    "pages_checked": report.pages_checked,
                    "findings": [f.__dict__ for f in report.findings],
                },
                fh,
                ensure_ascii=False,
                indent=2,
            )

    return 1 if any(f.level == "ERROR" for f in report.findings) else 0


if __name__ == "__main__":
    sys.exit(main())
