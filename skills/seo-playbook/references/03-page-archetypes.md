# 02 — Page archetypes

Every page must answer "what does it bring": signups, links, or topical
connectivity. Mixing archetypes produces pages that do none of the three.

## A. Free tool page

Commercial intent, leads to signup. The vidIQ model: tag generator, name
generator, hashtag generator. Competitive terms, but the intent is direct.

The limitation learned the hard way: these terms are usually held by DR 80+
sites, and at low authority the page sits at positions 30-60 for years. Worth
building, but do not budget traffic from it until DR rises.

## B. "What is trending now" hub

The freshness flagship, built on your own data. Its job is not traffic but
**citability**: this is the one archetype that actually earns links at zero
authority (the Exploding Topics model).

What makes a page citable — all of this was shipped:

- an anchor per item (`#trend-<id>`) with a self-link, so a specific row can be
  cited;
- a "Methodology" block explaining how the numbers are computed;
- a "Use this data" block with a ready-made citation line and permission to
  quote with a link;
- `Dataset` and `Article` JSON-LD;
- growth in numbers: "+X% week over week", "+N new this week";
- a soft CTA, not a sales banner.

On history: to compute week-over-week the snapshots must **accumulate**, not
overwrite. The write path was changed to append, pruning to the last N per
region. And a guard was added: show week-over-week only when the previous
snapshot is at least 5 days old, otherwise a same-day rebuild renders a lying
"+0%".

## C. Programmatic category and niche pages

A page per data slice: category × platform. Gives scale, but only on top of your
own data — see [03-programmatic.md](04-programmatic.md).

## D. Listicle hub

The hub as a ranking: "30 niches sorted by profitability and saturation".
Catches aggregate demand (rule 1 of the previous chapter) and distributes
authority to the per-item pages.

An important detail: two hubs for different platforms must **sort differently**
(YouTube by earning opportunity, TikTok short-form-native first), otherwise they
are duplicates of one list.

## E. Creator leaderboard

Programmatic on data about people. Cites well, is hard for a competitor to
fake, but requires an honest explanation of the growth metric.

## F. Educational cluster

Top of funnel and topical connectivity: a pillar plus spokes, all linking to
each other and into product pages. Implemented as a registry of slugs plus a
template per article, so adding an article costs one registry entry.

Tone decides. Write concretely, from your own data. The markers of AI slop —
generic paragraphs, stock examples — kill exactly the archetype whose job is to
prove expertise.

## The linking rule

The hub links to spokes, spokes link back to the hub and sideways to two or
three siblings, and every B and C page links to the nearest A page. That is how
a near-winner at position 12.7 gets pulled up by internal links rather than by
new content.
