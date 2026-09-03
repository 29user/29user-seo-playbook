# 08 — Text and file hygiene

When pages are written with a model, they carry junk that is invisible to the
eye: zero-width Unicode characters, exotic spaces, provenance marks in file
metadata. This is a technical problem, separate from the quality of the writing.

The approach is borrowed from
[watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover)
(stripping AI provenance marks) and applied narrowly: SEO has its own slice of
that problem, and it is not the same as that project's goal.

## What to take: deterministic removal of invisible characters

Models insert zero-width characters, soft hyphens, bidi marks and tag
characters. On a product site they land exactly where they do the most damage:

- in `title` and `description` — the engine prints them as-is, and the counted
  length disagrees with the visible one;
- in JSON-LD — the structured-data validator trips over an invisible character
  inside a string;
- in slugs and anchors — the link looks right and does not resolve;
- in the reader's in-page search — the match is not found.

Fixed deterministically, with no AI: `../scripts/strip_invisible.py`. The rule is
to clean on the way in, where text enters the template or the database, not
after the fact on rendered pages.

Do not overdo it: emoji sequences are held together by the same control
characters (ZWJ, variation selector), and blind removal breaks them. The script
accounts for this — joiners inside emoji are preserved, and so is the
non-breaking space, which is meaningful typography.

## What to take partially: file metadata

For site images two things matter: EXIF/XMP carry weight and sometimes GPS
coordinates, and generator tags in HTML and front matter (`data-ai*`,
`generator`, AI keys) are simply junk in the markup. Removing them is harmless
and useful.

## What NOT to take: rewriting to defeat detectors

That project's second layer rewrites text until a statistical detector stops
seeing a watermark. For SEO that is a bad trade, and the authors say so
themselves: "rewording degrades the copy" — the rewrite replaces your wording
with the rewriter model's and flattens tone and precision. And "no tool can
honestly certify" that a vendor's detector will fail.

The practical argument is stronger than the theoretical one: search engines rank
by usefulness, not by provenance; an "AI content level" metric in a third-party
audit is a tool's observation, not a ranking factor. Degrading readable copy for
that number trades something real for something imaginary.

What actually sits behind an audit's "similar AI-generated content" flag is
templated pages differing by one substituted word. That is fixed with data, not
with rewriting — see the quality gates in [03-programmatic.md](04-programmatic.md).

## The boundary

Stripping provenance from **your own** content for hygiene is fine. Passing
generated text off as human-written where provenance is declared or matters
(academic, legal, medical publishing, platforms with disclosure rules) is not
the same thing, and this playbook does not propose it. Other people's files with
other people's signatures are not touched at all.

## Checklist

- [ ] Text is cleaned of invisible characters on the way into the template or DB.
- [ ] Rendered HTML contains no invisible characters — verified by a test.
- [ ] Images carry no EXIF/XMP; markup carries no generator or `data-ai*` tags.
- [ ] Page uniqueness comes from data, not from rewriting one template.
