# 06 — Already paid for

Ideas that sound reasonable and were tested with real time and money. Before
proposing any of them again, bring a new fact, not new enthusiasm.

## Per-item long tail as a traffic source

28 pages, three months, zero impressions. The demand was elsewhere — see
[01-choose-surface.md](02-choose-surface.md).

## Entering a segment whose SERP is brand-held

Instagram: KD 0-2 with a top 10 of DR 55-96 sites. There was also no data source
and it is a direct competitor's home turf. The right move turned out to be a
one-hour demand probe instead of a one-to-two-month build.

## A western CDN in front of a site with a Russian-speaking audience

Since June 2025 Russian carriers throttle Cloudflare-fronted sites after the
first 16 KB. The landing HTML is about 21 KB, so pages would simply hang. A
second trap: "use a CDN with Russian PoPs" does not work either — those that
existed have left, and domestic ones do not serve the US. With two markets the
answer is not a shared CDN but an origin near each market, or geo-DNS.

## Moving to serverless hosting for speed

Checked and rejected separately: the database stays in the original region, so
every request pays a transatlantic round-trip, in-process caches evaporate, and
there is nowhere to run background jobs and the scheduler. Speed is fixed by a
nearby region on the same host.

## Fake trust signals in structured data

An invented 4.8/150 rating was removed from JSON-LD: a penalty risk, and a
direct contradiction of a product that sells itself as an honest data source.

## Expecting a technical fix to lift traffic

Speed, titles and health score are hygiene. They remove a ceiling on what
already ranks; they do not move a page from position 40 to page one. The only
lever for that is links.

## Reading traffic from Ahrefs

Systematically low. Take it as truth once and you will declare a page a failure
while Search Console shows it working.
