"""A meta description that fits the SERP whatever the entity name is.

Programmatic pages substitute a name into a template and the length drifts
unnoticed: a short name yields 152 characters, a long one 188. Half the pages
exceed the limit silently, and it only shows up in an audit weeks later.

The core is always printed; tails are appended only while they fit.
"""
from __future__ import annotations

MIN_LEN = 110
MAX_LEN = 160


def fit_description(core: str, extras: list[str], *, limit: int = MAX_LEN) -> str:
    out = core
    for extra in extras:
        candidate = f"{out} {extra}"
        if len(candidate) <= limit:
            out = candidate
    return out


def describe_entity(name: str, product: str = "Acme") -> str:
    """Example usage: a core that promises nothing, tails on the leftover budget."""
    return fit_description(
        f"{name} on YouTube: video ideas, rising sub-niches and the creators "
        f"growing fastest right now.",
        [f"See if the {name} niche is worth entering.", f"Free with {product}."],
    )
