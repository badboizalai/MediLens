"""CER and aggregation. CER = (S + D + I) / N chars, micro-averaged, NFC-normalised."""

from __future__ import annotations

import unicodedata
from collections import defaultdict


def normalize(text: str) -> str:
    """NFC + collapse all whitespace (OCR line breaks are not recognition errors)."""
    return " ".join(unicodedata.normalize("NFC", text).split())


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer_counts(ref: str, pred: str) -> tuple[int, int]:
    """Returns (edit distance, reference chars) after normalisation."""
    r, p = normalize(ref), normalize(pred)
    return levenshtein(r, p), len(r)


def _rate(rows: list[dict]) -> float | None:
    chars = sum(r["chars"] for r in rows)
    return sum(r["edits"] for r in rows) / chars if chars else None


def aggregate(rows: list[dict]) -> dict:
    """rows: {lang, quality, variant, edits, chars}. Micro-averaged CER overall and per group."""
    by_lang: dict[str, list[dict]] = defaultdict(list)
    by_quality: dict[str, list[dict]] = defaultdict(list)
    by_variant: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_variant[r["variant"]].append(r)
        by_lang[r["lang"]].append(r)
        by_quality[r["quality"]].append(r)
    return {
        "overall": _rate(rows),
        "by_lang": {k: _rate(v) for k, v in sorted(by_lang.items())},
        "by_quality": {k: _rate(v) for k, v in sorted(by_quality.items())},
        "by_variant": {k: _rate(v) for k, v in sorted(by_variant.items())},
    }
