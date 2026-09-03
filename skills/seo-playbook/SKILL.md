---
name: seo-playbook
description: Use when working on organic search for a website — setting up SEO from scratch, auditing why a site gets no search traffic, choosing which keywords or pages to build, planning programmatic/template-generated pages, fixing hreflang and multilingual markup, writing titles and meta descriptions at scale, checking a page before publishing, reviewing technical SEO before launch, interpreting Ahrefs or Search Console data, or judging whether an SEO idea is worth building. Also use when a health score dropped, pages are indexed but stuck on page 3-6, a new page is not getting indexed, or AI-written copy needs cleaning before it ships.
license: MIT
metadata:
  version: "1.0"
---

# SEO playbook

A step-by-step method for getting organic search traffic to a site with no
authority yet, plus runnable tools for the parts that can be checked
mechanically.

Written for someone doing SEO for the first time: every step says what to do,
which command verifies it, and when you are allowed to move on.

**The core claim:** for a site with low authority, outcomes are decided by
*which query you target*, not by how well you write. Head terms belong to large
established sites. Everything else here follows from that.

## Start with the roadmap

[references/00-roadmap.md](references/00-roadmap.md) is the spine: nine steps
from "we have a site and no traffic" to "we know what we are building and why".
Do not skip ahead to writing pages — steps 3 and 4 decide the outcome, and
everything else is preparation for them or cleanup after them.

| Step | What it settles | Detail |
|---|---|---|
| 1 | Make the site measurable (Search Console) | [00-roadmap](references/00-roadmap.md) |
| 2 | Where you actually stand | [01-diagnose](references/01-diagnose.md) |
| 3 | What people really search | [02-choose-surface](references/02-choose-surface.md) |
| 4 | Which battles you can win | [02-choose-surface](references/02-choose-surface.md) |
| 5 | Make the site indexable | [05-technical-checklist](references/05-technical-checklist.md) |
| 6 | Pick a page type and write it | [03-page-archetypes](references/03-page-archetypes.md) |
| 7 | Publish so it can be found | [04-programmatic](references/04-programmatic.md) for generated pages |
| 8 | Wait, then measure honestly | [06-measurement](references/06-measurement.md) |
| 9 | Earn links (the slow part) | [00-roadmap](references/00-roadmap.md) |

## Tools

Standard library only — no API key, no install. Both live in this skill's own
`scripts/` directory, so run them by the path this SKILL.md was loaded from:

```
python3 <skill-dir>/scripts/audit_site.py https://yourdomain.com
python3 <skill-dir>/scripts/preflight_page.py https://yourdomain.com/new-page/
```

When installed as a plugin, `<skill-dir>` sits under the marketplace and version,
so resolve it rather than typing it — for example:

```
SKILL_DIR=$(ls -d ~/.claude/plugins/cache/*/29user/*/skills/seo-playbook | tail -1)
python3 "$SKILL_DIR/scripts/audit_site.py" https://yourdomain.com
```

**`audit_site.py`** crawls the site's own sitemap and checks hreflang groups,
`x-default`, title and description lengths, duplicates, invisible Unicode,
`robots.txt` and `sitemap.xml` over GET, `www` versus bare host, `og:image`, and
orphan pages. Flags: `--limit N` (default 200), `--sitemap URL`, `--json PATH`.

**`preflight_page.py`** checks one page before it ships: metadata, canonical,
hreflang, JSON-LD (parses it, follows the images it references, flags invented
ratings), image alt text, internal links. Use `--local` on an unpublished file.

Both exit 1 on any ERROR. Severity does not encode blast radius — one missing
description and a site-wide template defect are both ERROR. Read the counts, not
just the exit code.

## From a finding to its explanation

| Reported | Read |
|---|---|
| `hreflang-*` | [05 — multilingual markup](references/05-technical-checklist.md) |
| `title`, `description`, `duplicate-*` | [05 — metadata](references/05-technical-checklist.md); [04](references/04-programmatic.md) if generated |
| `invisible-chars` | [08 — text hygiene](references/08-text-hygiene.md) |
| `host`, `robots`, `sitemap`, `orphan-page` | [05 — hosts and indexing](references/05-technical-checklist.md) |
| `og-image`, JSON-LD findings | [05 — social cards and structured data](references/05-technical-checklist.md) |
| `speed` | [07 — the CDN and serverless entries](references/07-antipatterns.md) |

## Rules that get violated by default

1. **Difficulty scores lie.** Two queries both at KD 0-2 can be opposite: one
   has an open result page, the other is held entirely by large publishers. Read
   the actual top ten before committing. One minute per query.

2. **Demand lives in aggregate queries, not per-item long tail.** People search
   "best X for Y", not "<specific item> X". Batches of per-item pages routinely
   return zero impressions for this reason alone.

3. **"Indexed but ranking 30-60" is an authority problem.** Rewriting the page
   does nothing; only links move it. Diagnose which problem you have before
   spending a week on the wrong one.

4. **Programmatic pages need your own data.** A shared template with a swapped
   noun is thin content. If the product cannot fill the page with something
   computed, do not generate the page.

5. **Probe demand before building a segment.** A fake-door page with `noindex`,
   kept out of the sitemap, plus one analytics event, costs an hour and can
   close a two-month build.

6. **Never hardcode `x-default` to the site home.** It puts a page that does not
   link back into every language group. One template line can break every page
   at once, invisibly.

7. **Technical fixes are hygiene, not growth.** They remove a ceiling on what
   already ranks. They do not move a page from position 40 to page one.

8. **Word count is not a lever.** "800 words per page" is a volume target, not a
   plan. Length follows from what the page has to show; if the only way to hit a
   count is padding, the page should not exist.

9. **Answer the question that was asked.** When someone proposes a plan, judge
   that plan first — including the possibility that the answer is "do not build
   this" — before offering a better one.

Before proposing anything, check it against
[07-antipatterns.md](references/07-antipatterns.md): approaches already tested
and found to fail.

## Code to copy into a project

| File | Fixes |
|---|---|
| [assets/hreflang_head.html.j2](assets/hreflang_head.html.j2) | Closed language groups, correct `x-default`, pages with no translation |
| [assets/fit_description.py](assets/fit_description.py) | Descriptions that stay in 110-160 chars whatever the entity name |
| [assets/sitemap_hreflang.py](assets/sitemap_hreflang.py) | Sitemap alternates built by the same rule as the HTML |
| [assets/test_seo_invariants.py](assets/test_seo_invariants.py) | Pytest invariants so the above cannot regress |
| [scripts/strip_invisible.py](scripts/strip_invisible.py) | Invisible Unicode from model-written copy, without breaking emoji |

## The part this does not solve

Link building as a practice. It is the binding constraint in every diagnosis
here. Step 9 of the roadmap says what can honestly be said about starting —
build something worth citing, claim the listings that apply, answer journalist
queries — and how long to expect to wait. Anything beyond that is outside what
this playbook verified; do not present untested tactics as proven.
