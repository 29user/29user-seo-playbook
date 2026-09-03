#!/usr/bin/env python3
"""Prove the reusable code does what the references claim it does.

These are the claims a reader will copy into their own project, so they are
verified here rather than asserted in prose.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "assets"), str(ROOT / "scripts")]

from fit_description import describe_entity, fit_description  # noqa: E402
from sitemap_hreflang import url_entry  # noqa: E402
from strip_invisible import find_invisible, strip_invisible  # noqa: E402


def check(label: str, condition: bool) -> None:
    print(f"{'ok  ' if condition else 'FAIL'} {label}")
    if not condition:
        sys.exit(1)


# Descriptions stay inside the SERP budget for both a short and a long name —
# the exact case where a single template silently overflows.
for name in ("Cars", "Health and wellness", "Do-it-yourself home renovation"):
    length = len(describe_entity(name))
    check(f"description for {name!r} is {length} chars, within 110-160",
          110 <= length <= 160)

check("a tail that does not fit is dropped, not truncated",
      fit_description("A" * 100, ["B" * 40, "C" * 5], limit=120) == "A" * 100 + " " + "C" * 5)

# x-default follows the page, and a page without a translation declares no
# alternate for the other language.
paired = url_entry("https://x.com/ru/a/", "https://x.com/en/a/", "ru", lastmod="2026-01-01")
check("x-default on a RU page points at its EN counterpart",
      'hreflang="x-default" href="https://x.com/en/a/"' in paired)

lonely = url_entry("https://x.com/en/only/", None, "en", lastmod="2026-01-01")
check("a page with no translation declares no ru alternate",
      'hreflang="ru"' not in lonely
      and 'hreflang="x-default" href="https://x.com/en/only/"' in lonely)

# Invisible characters go; emoji sequences and meaningful typography stay.
check("zero-width space and soft hyphen removed",
      strip_invisible("A​B­C") == "ABC")
check("emoji ZWJ sequence survives",
      strip_invisible("\U0001F468‍\U0001F469‍\U0001F467 x") == "\U0001F468‍\U0001F469‍\U0001F467 x")
check("variation selector after emoji survives",
      strip_invisible("⚠️ alert") == "⚠️ alert")
check("non-breaking space is kept",
      strip_invisible("100 km") == "100 km")
check("tag characters removed",
      strip_invisible("tag\U000E0041hidden") == "taghidden")
check("find_invisible reports position and code point",
      find_invisible("dirty​here") == [(5, "U+200B")] and find_invisible("clean") == [])


# --- audit checks that do not need the network ---------------------------------
from audit_site import Page, Report, check_orphans, check_duplicates  # noqa: E402


def _page(url: str, html: str) -> Page:
    return Page(url=url, status=200, html=html, final_url=url)


linked_html = '<html><head><title>Hub</title></head><body><a href="/a/">a</a></body></html>'
pages = {
    "https://s.com/": _page("https://s.com/", linked_html),
    "https://s.com/a/": _page("https://s.com/a/", "<html><head><title>A</title></head><body></body></html>"),
    "https://s.com/lonely/": _page("https://s.com/lonely/", "<html><head><title>L</title></head><body></body></html>"),
}
rep = Report()
check_orphans(pages, rep)
orphans = {f.url for f in rep.findings if f.check == "orphan-page"}
check("a page nothing links to is reported as an orphan",
      orphans == {"https://s.com/lonely/"})

rep2 = Report()
same = '<html><head><title>Same</title><meta name="description" content="d"></head></html>'
check_duplicates({"https://s.com/x/": _page("https://s.com/x/", same),
                  "https://s.com/y/": _page("https://s.com/y/", same)}, rep2)
check("identical titles across pages are reported once",
      len([f for f in rep2.findings if f.check == "duplicate-title"]) == 1)

print("\nall self-tests passed")
