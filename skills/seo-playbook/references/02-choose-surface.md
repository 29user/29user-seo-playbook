# 01 — Choosing a surface at low authority

The most expensive step. A mistake here does not cost a rewrite, it costs
months: 28 niche pages were built and returned zero impressions in three months
— not because they were bad pages, but because nobody types those queries.

## Rule 1. Demand lives in aggregates, not in the long tail

The intuition "a page per item, the long tail adds up" failed in practice.
People search in lists:

| Query | Volume/mo (US) | KD |
|---|---|---|
| `youtube niches` | 300 | 10 |
| `best youtube niches` | 100 | 9 |
| `most profitable youtube niches` | 150 | 20 |
| `asmr niche youtube` (per-item) | ~0 | — |

The fix: the hub becomes a **listicle** ("30 niches ranked by profitability"),
and per-item pages stay as an internal-link mesh and as landing pages for
navigational traffic, not as the traffic source.

## Rule 2. KD lies — look at the DR of the actual top 10

Two queries both at KD 0-2 can be opposites:

- One had KD 1 and an unprotected SERP: **winnable by a brand-new site**.
- The other had KD 0-2, but the whole top ten belonged to established
  publishers at DR 55-96. No new site takes that, ever.

The check takes a minute: open the SERP and read the DR of the first ten
results. If they are all DR 47+, the query is closed regardless of the
difficulty number.

## Rule 3. Platform arbitrage

The same intent costs different amounts on different platforms, because
competition arrived at different times. TikTok queries turned out several times
cheaper than the YouTube equivalents at comparable volume (`tiktok niche ideas`
200/KD 0 versus `youtube niche ideas` 60/KD 7). If the product covers several
platforms, start where the SERP is youngest.

## Rule 4. Probe demand before building a segment

Before committing one to two months of work to a segment, ship a fake door: an
honest "under consideration, vote for it" page, `noindex`, kept out of the
sitemap, linked from the footer, with one analytics event on the CTA. Then the
signal decides, not the opinion.

That is how the Instagram segment was closed: three independent walls (no trends
API, SERP held by DR 55-96 brands, direct competitor's home turf) — and instead
of a build it cost an hour.

## Selection checklist

- [ ] Is there an aggregate query with volume, or are we inventing a long tail?
- [ ] What is the DR of the top 10 — actually, not by KD?
- [ ] Is there a platform where the same need is cheaper?
- [ ] Can the product fill the page with its own data, or will this be a rehash?
- [ ] For a new segment: is a demand probe running instead of a build?
