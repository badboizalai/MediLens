"""Terminology normaliser: abbreviation expansion and lab/vital name -> LOINC.

Dictionary driven (data/terminology). Never guesses: ambiguous abbreviations return every
candidate, and a lab name returns None when the unit disagrees, two codes tie or the score is
below THRESHOLD. No ICD-10 here (LIC-002 not approved, see icd.py).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache

import yaml

from ..anatomy.fdi import TERMINOLOGY_DIR, normalize

THRESHOLD = 0.85  # fuzzy cut-off; below it we abstain
TIE = 0.03  # two different codes this close are a tie -> abstain

# Unit spellings seen in VN/EN records -> UCUM. Case matters (G/L giga vs g/L gram).
_UNIT_SYNONYMS = {
    "G/L": "10*3/uL",
    "10^9/L": "10*3/uL",
    "x10^9/L": "10*3/uL",
    "10^3/uL": "10*3/uL",
    "K/uL": "10*3/uL",
    "mmHg": "mm[Hg]",
    "bpm": "/min",
    "lần/phút": "/min",
    "°C": "Cel",
    "µmol/L": "umol/L",
}


@dataclass(frozen=True)
class Expansion:
    vi: str
    en: str
    source: str  # "abbreviations" | "dental:<term_id>"


@dataclass(frozen=True)
class Match:
    code: str
    display: str
    confidence: float  # 1.0 exact alias, else difflib ratio


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize(text))


@lru_cache(maxsize=1)
def _abbreviations() -> dict[str, tuple[Expansion, ...]]:
    table: dict[str, list[Expansion]] = {}

    def add(abbr: str, e: Expansion) -> None:
        got = table.setdefault(_compact(abbr), [])
        if all((x.vi, x.en) != (e.vi, e.en) for x in got):
            got.append(e)

    for r in yaml.safe_load((TERMINOLOGY_DIR / "abbreviations.v1.yaml").read_text("utf-8")):
        for x in r["expansions"]:
            add(r["abbr"], Expansion(x["vi"], x["en"], "abbreviations"))
    for r in yaml.safe_load((TERMINOLOGY_DIR / "dental-terms.v1.yaml").read_text("utf-8")):
        for a in r["abbrev"]:
            add(a, Expansion(r["vi"], r["en"], f"dental:{r['term_id']}"))
    return {k: tuple(v) for k, v in table.items()}


def expand_abbreviation(text: str) -> list[Expansion]:
    """All full terms for an abbreviation; [] if unknown. More than one = ambiguous, caller decides."""
    return list(_abbreviations().get(_compact(text), ()))


def _key(text: str) -> str:
    """Lowercase, no diacritics/punctuation, tokens sorted ('Cholesterol HDL' == 'HDL-C cholesterol' order-free)."""
    return " ".join(sorted(re.sub(r"[^a-z0-9]+", " ", normalize(text)).split()))


@lru_cache(maxsize=1)
def _labs() -> tuple[tuple[str, str, str, tuple[str, ...]], ...]:
    with (TERMINOLOGY_DIR / "loinc-labs.v1.csv").open(encoding="utf-8", newline="") as f:
        return tuple(
            (
                r["loinc_num"],
                r["long_common_name"],
                r["ucum_unit"],
                tuple(map(_key, r["aliases"].split("|"))),
            )
            for r in csv.DictReader(f)
        )


@lru_cache(maxsize=1)
def _units() -> dict[str, str]:
    return {u.lower(): u for _, _, u, _ in _labs()}


def _unit(tok: str) -> str | None:
    tok = tok.rstrip(".,;")
    return _UNIT_SYNONYMS.get(tok) or _units().get(tok.lower())


def _split(text: str) -> tuple[str, str | None]:
    """Free text 'Glucose máu 5.6 mmol/L' -> ('Glucose máu', 'mmol/L'): drop values, lift the unit."""
    name, unit = [], None
    for tok in text.split():
        if u := _unit(tok):
            unit = unit or u
            continue
        num = re.match(r"^[<>=~]?\d+(?:[.,]\d+)?(.*)$", tok)
        if num and not num.group(1):
            continue
        if num and (u := _unit(num.group(1))):
            unit = unit or u
            continue
        name.append(tok)
    return " ".join(name), unit


def _score(q: str, alias: str) -> float:
    if q == alias:
        return 1.0
    # shortcut: difflib ratio stands in for embedding + rerank. Same token count, and every
    # differing token pair must itself be a near-match of >=5 chars, so short codes (ALT/AST),
    # subsets ('troponin' vs 'troponin T') and one swapped token ('hs' vs 'T') stay exact-only.
    # Upgrade: embedding retrieval over aliases + cross-encoder rerank once a labelled set justifies it.
    qt, at = q.split(), alias.split()
    if len(qt) != len(at) or any(
        x != y and (min(len(x), len(y)) < 5 or SequenceMatcher(None, x, y).ratio() < THRESHOLD)
        for x, y in zip(qt, at, strict=True)
    ):
        return 0.0
    return SequenceMatcher(None, q, alias).ratio()


def to_loinc(text: str, unit: str | None = None) -> Match | None:
    """Lab/vital name (optionally with value and unit in the text) -> LOINC, or None to abstain."""
    name, found = _split(text)
    if unit is not None:
        unit = _unit(unit) or unit.strip()
    unit = unit or found
    q = _key(name)
    if not q:
        return None
    scored = sorted(
        (
            (max(_score(q, a) for a in aliases), code, display)
            for code, display, u, aliases in _labs()
            if unit is None or u == unit
        ),
        reverse=True,
    )
    best = scored[0] if scored else None
    if not best or best[0] < THRESHOLD:
        return None
    if any(s >= best[0] - TIE and c != best[1] for s, c, _ in scored[1:]):
        return None  # tie between codes (e.g. glucose mg/dL vs mmol/L with no unit)
    return Match(best[1], best[2], round(best[0], 3))
