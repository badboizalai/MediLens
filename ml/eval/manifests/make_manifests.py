#!/usr/bin/env python3
"""Write sha256sum-compatible manifests for the golden sets.

Usage: python3 make_manifests.py [name ...]   (default: golden-v0 golden-v1)

Output: SHA256SUMS.<name> next to this script, lines "<sha256>  <path relative
to ml/eval/<name>>", sorted by path. Verify with verify_manifests.py.
"""

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent
DEFAULT = ("golden-v0", "golden-v1")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entries(dataset: Path) -> dict[str, str]:
    return {
        p.relative_to(dataset).as_posix(): sha256(p)
        for p in sorted(dataset.rglob("*"))
        if p.is_file()
    }


def main(argv: list[str]) -> int:
    for name in argv[1:] or DEFAULT:
        dataset = EVAL / name
        if not dataset.is_dir():
            print(f"missing dataset: {dataset}", file=sys.stderr)
            return 2
        e = entries(dataset)
        out = HERE / f"SHA256SUMS.{name}"
        out.write_text("".join(f"{h}  {rel}\n" for rel, h in sorted(e.items())), encoding="utf-8")
        print(f"{out.name}: {len(e)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
