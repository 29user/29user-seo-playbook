#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the Agent Skills specification.

Checked here rather than trusted, because a malformed name or an over-long
description makes the skill silently unloadable. Also validates the plugin
manifest, since the plugin name is what prefixes the skill when it is invoked
(`<plugin>:<skill>`).
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def check_plugin_manifest() -> None:
    """The manifest lives two levels up when the skill ships inside a plugin."""
    import json

    manifest = ROOT.parent.parent / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return  # standalone skill, nothing to check
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for field in ("name", "description", "version"):
        if not data.get(field):
            fail(f"plugin.json is missing {field}")
    if not NAME_RE.fullmatch(data["name"]):
        fail(f"plugin.json name is not a valid slug: {data['name']!r}")
    listed = {pathlib.Path(p).name for p in data.get("skills", [])}
    if ROOT.name not in listed:
        fail(f"plugin.json does not list this skill: {ROOT.name} not in {sorted(listed)}")
    print(f"OK: plugin={data['name']} invokes this skill as {data['name']}:{ROOT.name}")


def main() -> None:
    check_plugin_manifest()
    skill = ROOT / "SKILL.md"
    if not skill.exists():
        fail("SKILL.md is missing")

    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---"):
        fail("SKILL.md does not start with YAML frontmatter")

    frontmatter = text.split("---", 2)[1]
    fields = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", frontmatter, re.M))

    name = fields.get("name", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        fail(f"invalid name: {name!r}")
    if name != ROOT.name:
        print(f"WARN: name {name!r} differs from directory {ROOT.name!r} — "
              f"install path must be .../{name}")

    description = fields.get("description", "")
    if not description:
        fail("description is empty")
    if len(description) > 1024:
        fail(f"description is {len(description)} chars, max 1024")

    body_lines = len(text.splitlines())
    if body_lines > 500:
        fail(f"SKILL.md is {body_lines} lines, keep it under 500")

    for link in re.findall(r"\]\((?!https?://|#)([^)]+)\)", text):
        if not (ROOT / link).exists():
            fail(f"SKILL.md links to a missing file: {link}")

    print(f"OK: name={name} description={len(description)}ch body={body_lines} lines")


if __name__ == "__main__":
    main()
