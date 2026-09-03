"""Sitemap alternates, built by the same rule as the HTML.

A mismatch between the sitemap and the page markup shows up in an audit as a
broken hreflang setup, while the real cause is two independent implementations
of one rule.
"""
from __future__ import annotations


def url_entry(loc: str, alt_loc: str | None, lang: str, *, lastmod: str,
              changefreq: str = "weekly", priority: str = "0.7") -> str:
    alt_lang = "en" if lang == "ru" else "ru"
    # x-default is the default-language version of this same page; for a page
    # with no translation that is the page itself.
    default_loc = loc if lang == "en" else (alt_loc or loc)

    links = [f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{loc}"/>']
    if alt_loc:
        links.append(
            f'    <xhtml:link rel="alternate" hreflang="{alt_lang}" href="{alt_loc}"/>'
        )
    links.append(
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{default_loc}"/>'
    )
    body = "\n".join(links)
    return (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"{body}\n"
        "  </url>"
    )
