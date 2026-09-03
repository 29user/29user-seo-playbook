"""Invariants that catch the return of the silent defects.

All of them happened on a live domain and none of them are visible to the eye:
broken hreflang groups, descriptions outside 110-160, a sitemap that disagrees
with the HTML, invisible characters in markup.

To adapt: point APP_IMPORT at your ASGI app and list your own pages.
"""
from __future__ import annotations

import html
import re
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from myapp.main import app  # replace with your own application

MIN_LEN, MAX_LEN = 110, 160

# Language pairs plus a page with no counterpart — every branch of the template.
PAGES = ["/en/", "/de/", "/en/pricing/", "/de/pricing/", "/en/guides/example/"]

_ALT = re.compile(r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"')
_CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"')
_DESC = re.compile(r'<meta name="description" content="([^"]*)"')


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _page(client, path):
    resp = client.get(path)
    if resp.status_code != 200:
        return None
    body = resp.text
    canon = _CANON.search(body)
    return {
        "alts": {k: urlsplit(v).path for k, v in _ALT.findall(body)},
        "canonical": urlsplit(canon.group(1)).path if canon else None,
        "description": html.unescape(_DESC.search(body).group(1)) if _DESC.search(body) else "",
    }


def test_x_default_is_the_default_language_version_of_this_page(client):
    for path in PAGES:
        page = _page(client, path)
        if page is None:
            continue
        expected = page["alts"].get("en") or page["canonical"]
        assert page["alts"].get("x-default") == expected, path


def test_alternate_groups_are_reciprocal(client):
    for path in PAGES:
        page = _page(client, path)
        if page is None:
            continue
        for lang, target in page["alts"].items():
            if lang == "x-default" or target == path:
                continue
            other = _page(client, target)
            assert other is not None, f"{path}: alternate {target} does not resolve"
            back = other["alts"].get("en" if lang == "ru" else "ru")
            assert back == path, f"{path} -> {target}, but back-link is {back}"


def test_descriptions_fit(client):
    for path in PAGES:
        page = _page(client, path)
        if page is None:
            continue
        desc = page["description"]
        assert desc, f"{path}: no description"
        assert MIN_LEN <= len(desc) <= MAX_LEN, f"{path}: {len(desc)}"


def test_sitemap_agrees_with_html(client):
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    for entry in re.findall(r"<url>(.*?)</url>", resp.text, re.S):
        links = dict(
            re.findall(r'<xhtml:link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', entry)
        )
        if "x-default" not in links:
            continue
        expected = links.get("en") or re.search(r"<loc>([^<]+)</loc>", entry).group(1)
        assert links["x-default"] == expected


def test_robots_and_sitemap_answer_get(client):
    # Test GET specifically: routes are often registered GET-only, and a HEAD
    # probe will lie with a 404 on a file that actually serves.
    assert client.get("/robots.txt").status_code == 200
    assert client.get("/sitemap.xml").status_code == 200


def test_no_invisible_characters_in_markup(client):
    # Invisible characters arrive with model-written copy and break length
    # budgets, structured-data validation and in-page search. See
    # scripts/strip_invisible.py in the playbook.
    from strip_invisible import find_invisible  # vendor it into your project

    for path in PAGES:
        resp = client.get(path)
        if resp.status_code != 200:
            continue
        head = resp.text.split("</head>", 1)[0]
        hits = find_invisible(head)
        assert not hits, f"{path}: invisible characters in <head> — {hits[:5]}"
