# 00 — Measure before strategising

One hour of work. Skip it and every plan is guesswork, and every progress report
is self-deception.

## What to record

| Metric | Source | Why it matters |
|---|---|---|
| Domain Rating, referring domains | Ahrefs Site Explorer | Decides which queries are reachable at all |
| Clicks and impressions by country, 3 months | Google Search Console | The only truth about traffic |
| Position for target queries | Search Console, not Ahrefs | Reveals "relevant but not authoritative" |
| DR of the actual top 10 for 5-10 money queries | Ahrefs SERP overview | The real height of the wall |
| Technical health score | Ahrefs Site Audit (or `scripts/audit_site.py`) | Catches template defects that break silently |

## The fork in the diagnosis

There are two entirely different versions of "we are invisible", and they are
treated in opposite ways:

1. **Pages are not in the index** — a technical problem, or content rendered
   client-side. Fixable by engineering, quickly.
2. **Pages are indexed, matched to the right queries, and sit at positions
   30-60** — an authority problem. No amount of rewriting fixes it.

On the reference project the second case looked like this: an influencer-
discovery page had 492 US impressions, 0 clicks, average position 40. Google
understood the page and still would not put it on page one. The correct
conclusion was not "rewrite the page" but "we have nothing to win this SERP
with".

## Near-winners: the cheapest available gain

List separately every query sitting at positions 8-20. These need a nudge, not a
new page, and internal links from existing pages can supply it. On the reference
project one query sat at 12.7, and thirty niche pages were wired to link to it.

## Ahrefs versus Search Console

Do not confuse their roles or the measurement will lie:

- **Search Console is the truth about traffic** — impressions, clicks,
  positions, countries.
- **Ahrefs is the truth about links and technical state.** Its traffic estimate
  is systematically low: it reported 24 visits per month where Search Console
  showed hundreds of clicks per quarter. Never compute conversion from it.

Ahrefs can also simply not see recent pages: a batch of 74 pages was about half
crawled a week after launch. Hence the waiting windows in
[05-measurement.md](06-measurement.md).
