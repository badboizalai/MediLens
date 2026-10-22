#!/usr/bin/env python3
"""Generate docs/agents/skill-catalog.md from .claude/skills/*/SKILL.md frontmatter."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"
OUT = ROOT / "docs" / "agents" / "skill-catalog.md"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        raise ValueError(f"{path}: missing frontmatter")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_-]+:", line):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def main() -> int:
    rows = []
    for skill in sorted(SKILLS.glob("medilens-*/SKILL.md")):
        fm = frontmatter(skill)
        desc = fm.get("description", "")
        first = re.split(r"(?<=[.])\s", desc, maxsplit=1)[0]
        rows.append(f"| `{fm['name']}` | {first} |")
    OUT.write_text(
        "# Skill catalog (generated — do not edit)\n\n"
        "Run `python3 tools/build_skill_index.py` to refresh.\n\n"
        "| Skill | Summary |\n| --- | --- |\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
