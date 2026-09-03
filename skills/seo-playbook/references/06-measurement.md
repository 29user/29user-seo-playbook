# 05 — How to measure

## Roles of the sources

| Source | Responsible for | Do not trust it for |
|---|---|---|
| Search Console | clicks, impressions, positions, countries | — |
| Ahrefs Site Explorer | links, DR, competitors | traffic estimates (low by multiples) |
| Ahrefs Site Audit | technical state | recency: the crawl may have hit a deploy |
| Product analytics | what the visitor does | attribution without campaign tagging |

## Waiting windows

The most common error is judging early and killing something that had no time.

- A new page: **8-12 weeks** before a verdict. Earlier, check indexing only.
- A technical fix: the next crawl, usually **one or two days**.
- A link: the first real one takes **about a month** of effort; its effect on
  clicks, three to four months.

## What counts as success at each horizon

1. **Week one**: pages indexed, health score clean, no position drops.
2. **Month one**: impressions appear for target queries (not brand ones), and
   average position moves down as a number.
3. **Quarter one**: clicks on non-brand queries; near-winners reach page one.

Separating brand from non-brand traffic is mandatory: on the reference project
almost every US click was for the brand name, meaning SEO brought nobody new
while the report looked alive.

## Reading a technical audit

Health score is the share of pages without errors, so read it as arithmetic
first: a score of 30 means roughly 70% of crawled pages carry at least one
error. That many pages do not break individually — that is a defect in something
shared, a template or a site-wide setting, and it lives in `<head>` where no
amount of clicking around will reveal it. Before inspecting pages one by one,
ask what all of them have in common.

One defect in a shared template therefore looks like a catastrophe, and its fix
looks like a leap. On the
reference project it went 10 → 90 in one crawl after fixing a single line. Do
not be flattered: that is a return to baseline, not growth.

Artefacts not worth fixing:
- the crawl hit a deploy → a batch of "timed out" and derived errors; confirm
  with one response-time check and it clears on the next crawl;
- "redirect target changed" after a planned URL move;
- "pages dropped from top 10" on brand-new URLs — ranking noise.

## If you have API access to the audit tool

Do not assume the number has to come from a human reading a dashboard. When an
Ahrefs (or equivalent) integration is available, pull the issue list directly —
then cross-check it against the per-page export, because of the limitation
below.

## A limitation of the audit API

The issues endpoint returns at most 100 rows with no pagination, and categories
late in the alphabet are simply invisible — which is exactly where the defect
explaining the whole health-score collapse was hiding. When the dashboard
disagrees with the API, dig through the per-page export with the specific issue
fields instead.
