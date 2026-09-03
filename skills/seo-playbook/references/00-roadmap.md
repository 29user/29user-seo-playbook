# 00 — The roadmap

Nine steps from "we have a site and no search traffic" to "we know what we are
building and why". Each step names what to do, how to verify it, and when you
are allowed to move on.

Do them in order. The most common way to waste a quarter is to start at step 5
(write pages) without steps 2 and 3 (find out what people search and whether you
can win it).

---

## Step 1 — Make the site measurable

**Do:** Verify the site in [Google Search Console](https://search.google.com/search-console)
(the DNS or HTML-file method, whichever your host supports). Submit the sitemap
there. If you have no sitemap, that is step 4's problem — submit it later.

**Verify:** Search Console shows non-zero impressions within a few days. Zero
impressions after a week usually means the site is not indexed at all, which is
step 4, not a content problem.

**Done when:** you can read impressions, clicks and average position by page and
by country.

**Why first:** every later decision depends on data only Search Console has.
Third-party tools estimate; Search Console counts.

---

## Step 2 — Find out where you actually stand

**Do:** Run the audit and read [01-diagnose.md](01-diagnose.md).

```
python3 scripts/audit_site.py https://yourdomain.com
```

Then answer one question from Search Console data: are your pages **absent from
the index**, or **present but ranking 30-60**? These look identical from the
outside and are treated in opposite ways.

**Verify:** you can state which of the two you have, with a number: "12 pages
indexed, average position 42" or "3 of 40 pages indexed".

**Done when:** the audit shows no ERROR findings, and you know which of the two
problems you are solving.

**Common mistake:** rewriting page copy when the diagnosis is authority. Nothing
you write moves a page from position 40.

---

## Step 3 — Find what people actually search

**Do:** Collect the queries in your area, with volumes. Paid tools (Ahrefs,
Semrush) do this directly. Without them: Google autocomplete, "People also ask",
the "related searches" block at the bottom of a result page, and your own
Search Console query list — anything you already get impressions for is proven
demand.

Write the candidates into a list with three columns: query, monthly volume,
difficulty. Then read [02-choose-surface.md](02-choose-surface.md).

**Verify:** each candidate has a volume number next to it. A query with no
volume data is a guess, not a candidate.

**Done when:** you have 10-30 candidate queries with volumes.

**Common mistake:** inventing long-tail queries that sound reasonable. "Best X
for Y" is searched; "<specific item> X" usually is not. Demand lives in
aggregate queries.

---

## Step 4 — Discard the battles you cannot win

**Do:** For each candidate, open the actual search results and look at who holds
the top ten. If they are large established sites, the query is closed to you
regardless of what the difficulty score says. Keep only queries where the top
ten contains sites comparable to yours.

**Verify:** for every query you kept, you can name at least one result in the
top ten that is not a major brand.

**Done when:** the list is shorter — usually much shorter — and every survivor
has a visible weak spot.

**Common mistake:** trusting the difficulty score. Two queries at KD 0-2 can be
opposite: one has an open SERP, the other is held entirely by publishers you
cannot outrank. This check takes a minute per query and saves months.

---

## Step 5 — Make the site indexable before adding to it

**Do:** Fix everything the audit reports as ERROR. Read
[05-technical-checklist.md](05-technical-checklist.md) for what each one means.
Minimum viable state: `robots.txt` and `sitemap.xml` return 200 on GET, every
page has a self-referencing canonical, one `www`/bare host redirects to the
other, and if the site is multilingual, the language groups are closed.

**Verify:**

```
python3 scripts/audit_site.py https://yourdomain.com
```

**Done when:** the audit exits 0.

**Why before writing:** publishing onto a broken foundation multiplies the
defect. The same template flaw lands on every new page you add.

---

## Step 6 — Choose the page type, then write it

**Do:** Pick an archetype from [03-page-archetypes.md](03-page-archetypes.md)
for each surviving query. A tool page, a data page, a listicle hub and a guide
have different jobs; a page that mixes them does none of them.

Write it. Rules that apply to every page:

- One page per query cluster, not per keyword.
- `title` under 60 characters, `description` 110-160.
- The page must contain something a competitor cannot copy in an afternoon —
  your data, your screenshots, your numbers.
- Length follows from what you have to show. Padding to a word count is a sign
  the page should not exist.

**Verify:** before publishing, check the page in isolation:

```
python3 scripts/preflight_page.py https://yourdomain.com/new-page/
```

**Done when:** preflight is clean and you can say in one sentence what the page
gives the reader that the current top ten does not.

---

## Step 7 — Publish so the page can be found

**Do:** Add the page to the sitemap. Link to it from at least two existing
pages — a page nothing links to is effectively invisible. If it has translations,
wire the language alternates ([05-technical-checklist.md](05-technical-checklist.md)).

If you are generating pages from data rather than writing them individually, read
[04-programmatic.md](04-programmatic.md) first — it has the quality gates that
keep generated pages from being treated as thin.

**Verify:** re-run the site audit; the new URL appears in the crawl, has no
findings, and is reachable from other pages.

**Done when:** the page is in the sitemap, linked internally, and clean.

---

## Step 8 — Wait, then measure honestly

**Do:** Nothing, for eight to twelve weeks. Then read
[06-measurement.md](06-measurement.md) and check Search Console: impressions for
non-brand queries, average position, clicks.

**Verify:** separate brand from non-brand traffic. Clicks on your own company
name are not SEO working.

**Done when:** you can say whether the page earns non-brand impressions. If it
earns impressions but no clicks, it ranks too low — that is authority, step 9.
If it earns nothing at all after twelve weeks, the query choice was wrong —
back to step 3.

**Common mistake:** judging at two weeks and deleting something that had not
started. Or judging by a third-party traffic estimate instead of Search Console.

---

## Step 9 — Earn links, which is the slow part

**Do:** Accept that this is the constraint. Pages that deserve to rank and
cannot are waiting on authority, and authority is other people linking to you.

Realistic starting order: build one genuinely citable asset (archetype B in
[03-page-archetypes.md](03-page-archetypes.md)) so there is something to point
at; claim the directory and listing placements that apply to you; then answer
journalist queries in your field with your own data, which is the fastest route
to a genuine editorial link.

**Verify:** referring domains in any backlink tool, counted monthly.

**Done when:** it never is. Expect the first real link after about a month of
consistent effort and its effect on clicks three to four months later.

**Honest warning:** this playbook does not solve this step. It tells you where
to start and how long to expect to wait.

---

## If you only remember one thing

Steps 3 and 4 decide the outcome. A well-built page targeting a query nobody
searches, or one you cannot win, returns nothing no matter how good it is.
Everything else in this playbook is either preparation for those two steps or
cleanup after them.
