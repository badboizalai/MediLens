#!/usr/bin/env python3
"""Parse FDI tooth references from Vietnamese/English dental text.

Usage:
    python fdi_parser.py "Sâu răng 36 mặt nhai, mất R46; trám 34-36"
    python fdi_parser.py --test

Returns JSON list of {"fdi": "36", "dentition": "permanent", "surfaces": ["O"], "span": "..."}.
Handles: "răng 36", "R36", "36", ranges "34-36" (same quadrant), deciduous 51-85,
surface words (mặt nhai/gần/xa/ngoài/trong; occlusal/mesial/distal/buccal/lingual)
and letter codes (O, M, D, B, L, MO, MOD...).
"""
import json
import re
import sys

PERMANENT = {f"{q}{p}" for q in range(1, 5) for p in range(1, 9)}
DECIDUOUS = {f"{q}{p}" for q in range(5, 9) for p in range(1, 6)}
VALID = PERMANENT | DECIDUOUS

SURFACE_WORDS = {
    "mặt nhai": "O", "nhai": "O", "occlusal": "O",
    "mặt gần": "M", "gần": "M", "mesial": "M",
    "mặt xa": "D", "xa": "D", "distal": "D",
    "mặt ngoài": "B", "ngoài": "B", "buccal": "B", "má": "B",
    "mặt trong": "L", "trong": "L", "lingual": "L", "lưỡi": "L", "palatal": "L",
}
TOKEN = re.compile(r"(?<![\d/.,])(?:(?:răng|rang|tooth|r)\s*)?(\d)(\d)(?:\s*[-–]\s*(\d)(\d))?(?![\d/.,]\d|\d)", re.IGNORECASE)
LETTERS = re.compile(r"\b([MODBL]{1,5})\b")


def surfaces_near(text: str, start: int, end: int) -> list[str]:
    window = text[end:end + 25].lower()
    found = []
    for word, code in sorted(SURFACE_WORDS.items(), key=lambda kv: -len(kv[0])):
        if word in window and code not in found:
            found.append(code)
    m = LETTERS.search(text[end:end + 8])
    if m:
        for ch in m.group(1):
            if ch not in found:
                found.append(ch)
    return found


def parse(text: str) -> list[dict]:
    results = []
    for m in TOKEN.finditer(text):
        q, p, q2, p2 = m.groups()
        start_code = f"{q}{p}"
        if start_code not in VALID:
            continue
        before = text[max(0, m.start() - 1):m.start()]
        if before.isdigit():
            continue
        codes = [start_code]
        if q2 and p2 and q2 == q:
            lo, hi = sorted((int(p), int(p2)))
            codes = [f"{q}{i}" for i in range(lo, hi + 1) if f"{q}{i}" in VALID]
        surf = surfaces_near(text, m.start(), m.end())
        for c in codes:
            results.append({
                "fdi": c,
                "dentition": "deciduous" if c in DECIDUOUS else "permanent",
                "surfaces": surf,
                "span": text[m.start():m.end()],
            })
    seen, unique = set(), []
    for r in results:
        if r["fdi"] not in seen:
            seen.add(r["fdi"])
            unique.append(r)
    return unique


def _test() -> None:
    cases = {
        "Sâu răng 36 mặt nhai": ["36"],
        "mất R46, trám 34-36": ["46", "34", "35", "36"],
        "răng 55 sâu": ["55"],
        "Tooth 19 is not valid": [],
        "BP 120/80, răng 11": ["11"],
        "36 MOD": ["36"],
    }
    for text, expected in cases.items():
        got = [r["fdi"] for r in parse(text)]
        assert got == expected, (text, got, expected)
    assert parse("36 MOD")[0]["surfaces"] == ["M", "O", "D"]
    assert parse("Sâu răng 36 mặt nhai")[0]["surfaces"] == ["O"]
    print("all tests passed")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _test()
    else:
        print(json.dumps(parse(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
