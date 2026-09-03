# 03 — Programmatic pages on product data

Programmatic works when each page shows something a competitor does not have:
your own computed data. Without that it is a farm of thin pages.

## The architecture that held up

- **One template with a platform/type parameter**, not a template per variant.
  One niche-hub template served both the YouTube and the TikTok hub.
- **A registry of entities in code** (a dict of slugs with data) plus
  `resolve(slug, lang)` returning the ready page context. Adding a page is a
  registry entry.
- **A dynamic route** `/{lang}/{section}/{slug}/` plus a 301 from the
  no-trailing-slash variant.
- **Sitemap generated from the same registry**, so the map cannot drift from the
  routes.

## Render on the server only

A page assembled by JavaScript in the browser does not exist for this purpose.
A trap worth naming: the SPA had a route that visually reproduced the landing
page, and it is easy to mistake it for the production page. Rule: anything that
must be indexed lives in a server template; the product UI lives separately.

## Freshness and caching

A live database query on every render is unnecessary and dangerous: it is the
one place where marketing pages can exhaust the shared connection pool. The data
was moved to a baked snapshot (a weekly job writes a ready slice, pages read a
single row) with a fallback to the live query until the first snapshot exists.

## Quality gates (mandatory, or thin-content problems follow)

- **A fill threshold**: if a slice has less data than the minimum, the page is
  not published or is marked `noindex`. An empty templated page is worse than no
  page.
- **Self-referencing canonical** on every slice page; never canonical to the hub.
- **No page per ephemeral entity** (one trend = one page) — that is a doorway.
  The right unit is a category or a period (dated weekly archives).
- **Slices must differ in substance**, not in word order in the heading.

## Compute title and description length programmatically

Programmatic substitutes an entity name into a template and the length drifts
unnoticed: "Cars" produced a 152-character description while "Health and
wellness" produced 188 — half the pages silently exceeded the limit.

The fix is assembly with a length budget: the core always, tails appended only
while they fit (`../assets/fit_description.py`). Same for titles: keep them
under 60 characters or Google rewrites them and the audit flags the mismatch.

## Internal link mesh

Generated, not hand-placed: every slice page gets links to two or three siblings
in its category, to its hub, and to the nearest conversion page. This is also
the only cheap way to pull up near-winners.
