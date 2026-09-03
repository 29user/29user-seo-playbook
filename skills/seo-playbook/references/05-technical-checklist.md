# 04 — Technical checklist

Everything here breaks silently: the site looks fine, pages render, and the
audit reports a failure. Every item was caught on a live domain.

Run `python3 scripts/audit_site.py <url>` to check most of this automatically.

## Multilingual markup

- [ ] `hreflang` declarations are **reciprocal**: if A names B, B names A.
- [ ] `x-default` points at the **default-language version of this same page**,
      not at the site home.
- [ ] A page with no translation **declares no alternate** — better none than a
      link to the home page.
- [ ] The language switcher may fall back to the home page; `hreflang` may not.
      They are different things.

Cost of the mistake: a single hardcoded `x-default` can put every page on the
site into a broken group at once. Health scores collapse, Google stops
connecting the language versions, and clicking around the site shows nothing
wrong — the defect lives entirely in `<head>`.

## Metadata

- [ ] `title` ≤ 60 characters, or the engine rewrites it.
- [ ] `description` between 110 and 160 characters on **every** page, generated
      ones included.
- [ ] The description is in the page's own language. Legal pages are the usual
      offender.
- [ ] The SPA/app domain needs a description too — it gets forgotten because it
      is "not for SEO".

## Indexing and sitemap

- [ ] `robots.txt` and `sitemap.xml` return 200 on **GET** — test GET, not HEAD:
      routes are often registered GET-only and `curl -I` will lie with a 404.
- [ ] The sitemap lists only canonical URLs returning 200, with no redirect
      chains.
- [ ] `x-default` in the sitemap agrees with the HTML.

## Hosts and domains

- [ ] `www` either is served and 301s to the bare domain, or does not resolve at
      all. The worst state is in between: a DNS record exists while the host is
      not served, so the connection is dropped and the audit reports
      "robots.txt is not accessible".
- [ ] A certificate covers every host that resolves.

## Social cards and structured data

- [ ] The OG image actually resolves. On the reference project it 404'd for
      months — and the same URL was referenced as `screenshot` inside JSON-LD,
      which failed structured-data validation on every page.
- [ ] No invented ratings in structured data. A fake `aggregateRating` is both a
      penalty risk and a direct contradiction of "we are an honest data source".

## Speed and geography

- [ ] Know where the crawler measures from: a single European origin gave ~950ms
      to the US versus ~200ms within Europe. The fix is an origin near the target
      market, not rewriting pages.
- [ ] Cache headers without a CDN are browser-only. A pass-through proxy speeds
      up nothing for a crawler.

## Invariants in tests

All of the above belongs in tests or it comes back. Working examples:
`../assets/test_seo_invariants.py`.
