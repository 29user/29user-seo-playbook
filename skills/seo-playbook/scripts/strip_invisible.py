"""Deterministic removal of invisible characters from text headed for markup.

Models insert zero-width characters, soft hyphens, bidi marks and tag characters.
They are invisible to the eye, but in title/description they break the length
budget, in JSON-LD they break validation, in slugs they break the link, and in
the reader's in-page search they break the match.

The approach comes from https://github.com/guillaumemeyer/watermarks-remover
(layer A), reduced to what a product site needs. No rewriting of text: only
removal of characters that should not be there.

Emoji survive: the zero-width joiner and the variation selector are kept when
they sit inside an emoji sequence.
"""
from __future__ import annotations

import re
import unicodedata

ZWJ = "‍"
VS16 = "️"

# Characters that have no business in ordinary text.
_ALWAYS_DROP = {
    "​",  # zero-width space
    "‌",  # zero-width non-joiner
    "⁠",  # word joiner
    "﻿",  # BOM / zero-width no-break space
    "­",  # soft hyphen
    "᠎",  # mongolian vowel separator
    "᠏",
    "ㅤ",  # hangul filler
    "ﾠ",  # halfwidth hangul filler
    "⁥",  # reserved default-ignorable
}
# Bidirectional control characters.
_ALWAYS_DROP |= {chr(c) for c in range(0x202A, 0x202F)}
_ALWAYS_DROP |= {chr(c) for c in range(0x2066, 0x206A)}
# Tag characters — a carrier for hidden data inside an ordinary string.
_ALWAYS_DROP |= {chr(c) for c in range(0xE0000, 0xE0080)}
# Non-characters.
_ALWAYS_DROP |= {chr(c) for c in range(0xFDD0, 0xFDF0)}

# Exotic spaces -> a regular space. The non-breaking space stays: it is
# meaningful (French typography, "100 km"), and removing it damages the text.
_SPACES = {chr(c) for c in range(0x2000, 0x200B)} | {" ", " ", "　"}

_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF←-⇿⬀-⯿]"
)


def _is_emoji(ch: str | None) -> bool:
    return bool(ch) and bool(_EMOJI_RE.match(ch))


def strip_invisible(text: str, *, normalize_spaces: bool = True) -> str:
    """Remove invisible characters, preserving emoji and meaningful typography."""
    if not text:
        return text
    out = []
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else None
        nxt = text[i + 1] if i + 1 < len(text) else None

        if ch == ZWJ and _is_emoji(prev) and _is_emoji(nxt):
            out.append(ch)  # emoji glue — keep it
            continue
        if ch == VS16 and _is_emoji(prev):
            out.append(ch)  # emoji presentation of the previous character
            continue
        if ch == ZWJ or ch in _ALWAYS_DROP:
            continue
        if normalize_spaces and ch in _SPACES:
            out.append(" ")
            continue
        # Anything else in category Cf (format characters) is suspect, apart
        # from the cases handled above.
        if unicodedata.category(ch) == "Cf":
            continue
        out.append(ch)
    return "".join(out)


def find_invisible(text: str) -> list[tuple[int, str]]:
    """Positions and code points of suspect characters — for tests and reports."""
    hits = []
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else None
        nxt = text[i + 1] if i + 1 < len(text) else None
        if ch == ZWJ and _is_emoji(prev) and _is_emoji(nxt):
            continue
        if ch == VS16 and _is_emoji(prev):
            continue
        if ch == ZWJ or ch in _ALWAYS_DROP or unicodedata.category(ch) == "Cf":
            hits.append((i, f"U+{ord(ch):04X}"))
    return hits
