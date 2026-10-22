#!/usr/bin/env python3
"""Validate skills and agents: frontmatter, name == folder, referenced files exist."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".claude" / "agents"
CANONICAL = ROOT / "docs" / "agents" / "project-context.md"


def fm(path: Path) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return {}
    return {
        k.strip(): v.strip()
        for k, _, v in (ln.partition(":") for ln in m.group(1).splitlines() if re.match(r"^[A-Za-z_-]+:", ln))
    }


def main() -> int:
    errors: list[str] = []
    for skill in sorted(SKILLS.glob("medilens-*/SKILL.md")):
        d = skill.parent
        meta = fm(skill)
        if meta.get("name") != d.name:
            errors.append(f"{d.name}: frontmatter name {meta.get('name')!r} != folder")
        if len(meta.get("description", "")) < 50:
            errors.append(f"{d.name}: description missing/too short")
        for ref in set(re.findall(r"`((?:references|assets|scripts)/[\w./-]+)`", skill.read_text(encoding="utf-8"))):
            if not (d / ref).exists():
                errors.append(f"{d.name}: referenced file missing: {ref}")
        ctx = d / "references" / "project-context.md"
        if ctx.exists() and ctx.read_bytes() != CANONICAL.read_bytes():
            errors.append(f"{d.name}: project-context.md out of sync (run tools/sync_skill_context.py)")
    for agent in sorted(AGENTS.glob("*.md")):
        meta = fm(agent)
        for key in ("name", "description"):
            if not meta.get(key):
                errors.append(f"agent {agent.name}: missing {key}")
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
