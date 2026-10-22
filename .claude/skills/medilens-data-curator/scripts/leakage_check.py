#!/usr/bin/env python3
"""Detect overlap between two dataset folders (e.g. train vs golden).

Usage: python leakage_check.py <dir_a> <dir_b> [--text]

Hashes every file (SHA-256 of bytes; with --text, of normalised text:
lower-case, collapsed whitespace, for .txt/.json/.md/.csv) and reports files
whose hash appears in both folders. Exit 1 when any overlap is found.
"""
import hashlib
import os
import re
import sys

TEXT_EXT = {".txt", ".json", ".md", ".csv"}


def digest(path, text_mode):
    if text_mode and os.path.splitext(path)[1].lower() in TEXT_EXT:
        with open(path, encoding="utf-8", errors="replace") as fh:
            norm = re.sub(r"\s+", " ", fh.read().lower()).strip()
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index(folder, text_mode):
    out = {}
    for root, _d, files in os.walk(folder):
        for f in files:
            p = os.path.join(root, f)
            out.setdefault(digest(p, text_mode), []).append(os.path.relpath(p, folder))
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    text_mode = "--text" in argv
    a, b = [x for x in argv[1:] if not x.startswith("--")][:2]
    ia, ib = index(a, text_mode), index(b, text_mode)
    common = set(ia) & set(ib)
    print(f"{a}: {sum(len(v) for v in ia.values())} files · {b}: {sum(len(v) for v in ib.values())} files · overlap: {len(common)}")
    for h in sorted(common):
        print(f"  {ia[h][0]}  <->  {ib[h][0]}")
    print("RESULT:", "FAIL (leakage)" if common else "PASS")
    return 1 if common else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
