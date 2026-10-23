#!/usr/bin/env python3
"""Verify golden-set manifests; exit 1 on any mismatch, missing or extra file.

Usage: python3 verify_manifests.py [name ...]   (default: golden-v0 golden-v1)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_manifests as mk  # noqa: E402


def parse(manifest: Path) -> dict[str, str]:
    out = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, _, rel = line.partition("  ")
        out[rel] = digest
    return out


def verify(name: str) -> list[str]:
    manifest = mk.HERE / f"SHA256SUMS.{name}"
    dataset = mk.EVAL / name
    if not manifest.is_file() or not dataset.is_dir():
        return [f"{name}: manifest or dataset missing"]
    want, have = parse(manifest), mk.entries(dataset)
    errors = [f"{name}: MISSING {r}" for r in sorted(want.keys() - have.keys())]
    errors += [f"{name}: EXTRA {r}" for r in sorted(have.keys() - want.keys())]
    errors += [
        f"{name}: MISMATCH {r}" for r in sorted(want.keys() & have.keys()) if want[r] != have[r]
    ]
    return errors


def main(argv: list[str]) -> int:
    failed = False
    for name in argv[1:] or mk.DEFAULT:
        errors = verify(name)
        failed |= bool(errors)
        print(f"{name}: " + ("FAIL" if errors else "OK"))
        for e in errors:
            print("  " + e)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
