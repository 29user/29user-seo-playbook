# SEO playbook — a Claude Code skill

A Claude Code skill for SEO: a step-by-step method for getting organic search
traffic to a site that has no authority yet, with runnable audits for the parts
a script can check.

Works as an Agent Skill in Claude Code, and the audits run standalone as plain
Python if you just want the tools.

Written for a first-timer: [nine steps](skills/seo-playbook/references/00-roadmap.md), each one
saying what to do, which command verifies it, and when you may move on. Only
approaches that were actually tried are in here, including the ones that
failed.

## Install as a plugin

In Claude Code:

```
/plugin marketplace add 29user/29user-seo-playbook
/plugin install 29user
```

The skill is then invoked as `29user:seo-playbook`. Claude loads it on its own
when a task involves organic search — auditing a site, choosing keywords, fixing
hreflang, checking a page before it ships — and pulls in the relevant reference
file on demand.

Prefer a plain skill directory, without the plugin wrapper:

```bash
git clone https://github.com/29user/29user-seo-playbook /tmp/sp \
  && cp -r /tmp/sp/skills/seo-playbook ~/.claude/skills/seo-playbook
```

## Use the tools standalone

Python 3.10+, standard library only, no API key and nothing to install.

Audit a whole site — crawls its sitemap and reports the defects that are
invisible in a browser: broken hreflang groups, `x-default` hardcoded to the
home page, title and description lengths, duplicate metadata, invisible Unicode
characters, `robots.txt`/`sitemap.xml` unreachable over GET, a `www` host that
resolves but is not served, a broken `og:image`, and pages nothing links to:

```bash
python3 skills/seo-playbook/scripts/audit_site.py https://yourdomain.com
```

Check a single page before publishing it — metadata, canonical, hreflang,
JSON-LD (parsed, with its referenced images followed), image alt text, internal
links. Works on an unpublished file with `--local`:

```bash
python3 skills/seo-playbook/scripts/preflight_page.py https://yourdomain.com/new-page/
```

Both exit 1 on any ERROR, so either can gate CI.

## The claim in five lines

- **Below DR 20 the winner is query selection, not copy quality.** Head terms
  belong to DR 47-99 sites; only undefended SERPs are reachable.
- **Keyword difficulty lies.** Read the DR of the actual top 10 instead.
- **Demand lives in aggregate queries**, not in per-item long tail.
- **Programmatic scale only works on top of your own data.** Otherwise it is
  thin pages that get collapsed.
- **Links are the only lever that raises the ceiling.** Everything else moves
  positions underneath it.

## Contents

| Path | What it is |
|---|---|
| `.claude-plugin/` | Plugin and marketplace manifests — what makes the skill resolve as `29user:seo-playbook` |
| `skills/seo-playbook/SKILL.md` | Entry point for the agent: the step table, the tools, the rules that get violated by default |
| `skills/seo-playbook/references/00-roadmap.md` | The nine steps, in order |
| `skills/seo-playbook/references/` | One file per decision: diagnosis, surface choice, page archetypes, programmatic, technical checklist, measurement, antipatterns, text hygiene |
| `skills/seo-playbook/scripts/` | `audit_site.py` (whole site), `preflight_page.py` (one page), `strip_invisible.py` (invisible Unicode) |
| `skills/seo-playbook/assets/` | Code to copy into a project: hreflang template, description length budget, sitemap alternates, pytest invariants |

## What it does not solve

Link building as a practice — outreach, digital PR, placement in other people's
listicles. It is named throughout as the binding constraint, and it is the part
this playbook does not solve. Any claim that it solves authority is false.

## Credits

The text-hygiene approach in `references/08-text-hygiene.md` and
`scripts/strip_invisible.py` is adapted from
[watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) by
Guillaume Meyer (MIT) — its deterministic layer only. The statistical-rewriting
layer is deliberately excluded; the reference file explains why.

## License

MIT — see [LICENSE](LICENSE).
