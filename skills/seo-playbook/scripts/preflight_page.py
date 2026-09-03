#!/usr/bin/env python3
"""Check one page before publishing it.

The site audit answers "is the site healthy". This answers "is this page ready",
which is the question you have while writing it. Standard library only.

    python3 preflight_page.py https://example.com/new-page/
    python3 preflight_page.py page.html --local

Exit code is 1 if anything blocking is found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from audit_site import (  # noqa: E402
    CANON_RE,
    DESC_MAX,
    DESC_MIN,
    DESC_RE,
    H1_RE,
    OG_IMAGE_RE,
    TITLE_MAX,
    TITLE_RE,
    alternates,
    fetch,
    first,
    invisible_hits,
)

JSONLD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I
)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
ALT_ATTR_RE = re.compile(r'\balt\s*=\s*["\'][^"\']*["\']', re.I)


def report(level: str, message: str) -> tuple[str, str]:
    return (level, message)


def check_structured_data(head: str, page_url: str) -> list[tuple[str, str]]:
    """Structured data fails quietly: the page renders, the rich result does not.

    The two failures worth catching without a validator are invalid JSON and a
    referenced image that does not exist — the second one broke validation
    site-wide on a real project because the same URL was in every page.
    """
    out: list[tuple[str, str]] = []
    blocks = JSONLD_RE.findall(head)
    if not blocks:
        out.append(report("INFO", "no JSON-LD on the page"))
        return out

    for raw in blocks:
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError as exc:
            out.append(report("ERROR", f"JSON-LD does not parse: {exc}"))
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            kind = item.get("@type", "(no @type)")
            if "@context" not in item and not isinstance(data, list):
                out.append(report("WARN", f"JSON-LD {kind}: no @context"))

            # Invented ratings are a policy risk and undercut any claim of being
            # a trustworthy source.
            if "aggregateRating" in item:
                out.append(report(
                    "WARN",
                    f"JSON-LD {kind}: declares aggregateRating — only keep it if "
                    f"the ratings are real and visible on the page",
                ))

            for field in ("image", "logo", "screenshot", "thumbnailUrl"):
                value = item.get(field)
                if isinstance(value, dict):
                    value = value.get("url")
                if isinstance(value, str) and value.startswith("http"):
                    probe = fetch(value)
                    if probe.status != 200:
                        out.append(report(
                            "ERROR",
                            f"JSON-LD {kind}.{field} -> {probe.status or probe.error}: {value}",
                        ))
            out.append(report("INFO", f"JSON-LD {kind}: parsed"))
    return out


def check_links(html: str, page_url: str) -> list[tuple[str, str]]:
    """Internal links are how a new page gets discovered and how near-winners
    get pulled up. A page that links nowhere and is linked from nowhere is
    invisible regardless of its content."""
    out: list[tuple[str, str]] = []
    host = urlsplit(page_url).netloc
    hrefs = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']', html, re.I)
    internal = set()
    for href in hrefs:
        if href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        absolute = urljoin(page_url, href)
        if urlsplit(absolute).netloc == host:
            internal.add(absolute.split("#")[0])
    internal.discard(page_url)
    internal.discard(page_url.rstrip("/"))

    if len(internal) < 3:
        out.append(report(
            "WARN",
            f"only {len(internal)} internal link(s) — link to related pages so "
            f"crawlers and readers can move on from here",
        ))
    else:
        out.append(report("INFO", f"{len(internal)} internal links"))
    return out


def check_images(html: str) -> list[tuple[str, str]]:
    tags = IMG_RE.findall(html)
    if not tags:
        return []
    missing = [t for t in tags if not ALT_ATTR_RE.search(t)]
    if missing:
        return [report("WARN", f"{len(missing)} of {len(tags)} <img> without alt text")]
    return [report("INFO", f"{len(tags)} images, all with alt text")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check one page before publishing.")
    parser.add_argument("page", help="page URL, or a file path with --local")
    parser.add_argument("--local", action="store_true", help="read a local HTML file")
    args = parser.parse_args()

    if args.local:
        html = open(args.page, encoding="utf-8").read()
        page_url = "https://example.invalid/local-file/"
        print(f"Preflight — {args.page} (local file)\n")
    else:
        url = args.page if args.page.startswith("http") else f"https://{args.page}"
        page = fetch(url)
        if page.status != 200:
            print(f"Preflight — {url}\n\n[ERROR] page returns {page.status or page.error}")
            return 1
        html, page_url = page.html, page.final_url or url
        print(f"Preflight — {page_url}\n")

    head = html.split("</head>", 1)[0]
    findings: list[tuple[str, str]] = []

    title = first(TITLE_RE, head)
    if not title:
        findings.append(report("ERROR", "no <title>"))
    elif len(title) > TITLE_MAX:
        findings.append(report("WARN", f"title is {len(title)} chars (>{TITLE_MAX}): {title!r}"))
    else:
        findings.append(report("INFO", f"title {len(title)} chars"))

    desc = first(DESC_RE, head)
    if desc is None:
        findings.append(report("ERROR", "no meta description"))
    elif not (DESC_MIN <= len(desc) <= DESC_MAX):
        findings.append(report("WARN", f"description is {len(desc)} chars, want {DESC_MIN}-{DESC_MAX}"))
    else:
        findings.append(report("INFO", f"description {len(desc)} chars"))

    canonical = first(CANON_RE, head)
    if not canonical:
        findings.append(report("WARN", "no canonical"))
    elif not args.local and canonical.rstrip("/") != page_url.rstrip("/"):
        findings.append(report(
            "WARN", f"canonical points elsewhere: {canonical} — intended only if this "
            f"page is a duplicate"))
    else:
        findings.append(report("INFO", "canonical is self-referencing"))

    h1s = len(H1_RE.findall(html))
    if h1s == 0:
        findings.append(report("WARN", "no <h1>"))
    elif h1s > 1:
        findings.append(report("INFO", f"{h1s} <h1> tags"))

    hits = invisible_hits(head)
    if hits:
        findings.append(report(
            "ERROR", f"{len(hits)} invisible character(s) in <head>: {', '.join(hits[:5])} "
            f"— run strip_invisible.py over the source copy"))

    alts = alternates(head)
    if alts:
        xdefault = alts.get("x-default")
        others = {v for k, v in alts.items() if k != "x-default"}
        if xdefault and xdefault not in others and xdefault.rstrip("/") != (canonical or "").rstrip("/"):
            findings.append(report(
                "ERROR", f"x-default={xdefault} is neither this page nor one of its "
                f"alternates — the usual cause is a hardcoded site home"))
        else:
            findings.append(report("INFO", f"{len(alts)} hreflang alternates"))

    og_image = first(OG_IMAGE_RE, head)
    if not og_image:
        findings.append(report("WARN", "no og:image — the page has no share card"))
    elif not args.local:
        probe = fetch(og_image)
        if probe.status != 200:
            findings.append(report("ERROR", f"og:image returns {probe.status or probe.error}"))
        else:
            findings.append(report("INFO", "og:image resolves"))

    findings += check_structured_data(head, page_url)
    findings += check_images(html)
    if not args.local:
        findings += check_links(html, page_url)

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for level, message in sorted(findings, key=lambda f: order[f[0]]):
        print(f"[{level}] {message}")

    errors = sum(1 for level, _ in findings if level == "ERROR")
    warns = sum(1 for level, _ in findings if level == "WARN")
    print(f"\n{errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
