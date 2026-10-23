"""FDI tooth-number parser. Valid numbers come from data/terminology/fdi.csv (52 teeth)."""

from __future__ import annotations

import csv
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

# shortcut: repo-relative path; override via env when the worker image ships data elsewhere.
TERMINOLOGY_DIR = Path(
    os.environ.get(
        "MEDILENS_TERMINOLOGY_DIR", Path(__file__).resolve().parents[5] / "data" / "terminology"
    )
)


class InvalidFdi(ValueError):
    """A tooth number that is not in the FDI table (e.g. 19, 49, 86)."""


def normalize(text: str) -> str:
    """Lowercase, strip diacritics (incl. d-stroke), collapse whitespace."""
    t = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip()


@lru_cache(maxsize=1)
def teeth() -> dict[str, str]:
    """fdi number -> laterality ('left'|'right'), patient's own side."""
    with (TERMINOLOGY_DIR / "fdi.csv").open(encoding="utf-8", newline="") as f:
        return {r["fdi"]: r["laterality"] for r in csv.DictReader(f)}


_N = r"\d{1,3}"
_ITEM = rf"{_N}(?:\s*(?:-|to|den)\s*{_N})?"
_EXPR = rf"{_ITEM}(?:\s*(?:,|;|/|&|va|and)\s*{_ITEM})*"
_MARKED = re.compile(rf"(?:\b(?:rang so|rang|tooth|teeth|no\.?)\s*|#\s*|\br\s?(?=\d)){_EXPR}")
_BARE = re.compile(_EXPR)


def _expand(item: str) -> list[str]:
    nums = re.findall(_N, item)
    if len(nums) == 1:
        out = nums
    else:
        lo, hi = sorted(nums)
        if lo[0] != hi[0]:  # a range never crosses quadrants
            raise InvalidFdi(item)
        out = [str(n) for n in range(int(lo), int(hi) + 1)]
    bad = [n for n in out if n not in teeth()]
    if bad:
        raise InvalidFdi(", ".join(bad))
    return out


def parse_fdi(text: str, *, dental_context: bool = False) -> list[str]:
    """FDI numbers in `text` ("răng 36", "tooth 36", "R36", "36, 37", "11-13"), in order.

    A bare number list is accepted only when `dental_context` and it is the whole text.
    Returns [] if no tooth reference; raises InvalidFdi for numbers not in the table.
    """
    t = normalize(text)
    spans = [m.group(0) for m in _MARKED.finditer(t)]
    if not spans and dental_context and _BARE.fullmatch(t):
        spans = [t]
    out: list[str] = []
    for s in spans:
        for item in re.findall(_ITEM, re.sub(r"^\D+", "", s)):
            out += [n for n in _expand(item) if n not in out]
    return out
