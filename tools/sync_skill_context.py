#!/usr/bin/env python3
"""Copy the canonical docs/agents/project-context.md into every skill's references/."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "agents" / "project-context.md"

for skill in sorted((ROOT / ".claude" / "skills").glob("medilens-*")):
    dst = skill / "references" / "project-context.md"
    dst.parent.mkdir(exist_ok=True)
    shutil.copyfile(SRC, dst)
    print("synced", dst.relative_to(ROOT))
