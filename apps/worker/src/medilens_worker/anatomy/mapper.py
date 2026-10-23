"""Free-text location -> region_code. Rules only; codes come from region-tree.v1.yaml."""

from __future__ import annotations

import re
from functools import lru_cache

import yaml

from .fdi import TERMINOLOGY_DIR, InvalidFdi, normalize, parse_fdi

_SIDE = {
    "left": re.compile(r"\b(?:trai|left|lt)\b"),
    "right": re.compile(r"\b(?:phai|right|rt)\b"),
    "both": re.compile(r"\b(?:hai ben|2 ben|bilateral|both)\b"),
}


@lru_cache(maxsize=1)
def tree() -> dict[str, str | None]:
    """region_code -> parent."""
    rows = yaml.safe_load((TERMINOLOGY_DIR / "region-tree.v1.yaml").read_text("utf-8"))
    return {r["region_code"]: r["parent"] for r in rows}


@lru_cache(maxsize=1)
def concepts() -> list[tuple[list[str], dict[str, str]]]:
    rows = yaml.safe_load((TERMINOLOGY_DIR / "location-synonyms.v1.yaml").read_text("utf-8"))
    return [
        ([normalize(t) for t in r["terms"]], {k: r[k] for k in ("code", "right", "left") if k in r})
        for r in rows
    ]


def _side(t: str) -> str | None:
    """'left' | 'right' | 'ambiguous' | None (no side stated)."""
    found = {k for k, rx in _SIDE.items() if rx.search(t)}
    if not found:
        return None
    return found.pop() if len(found) == 1 and "both" not in found else "ambiguous"


def _resolve(codes: dict[str, str], side: str | None) -> tuple[str | None, float]:
    if side in ("left", "right") and side in codes:
        return codes[side], 0.9
    if "code" in codes:  # side-independent region (a stated side is ignored)
        return codes["code"], 0.9
    if side in ("left", "right"):
        parent = tree()[codes["right" if "right" in codes else "left"]]
        return parent, 0.5  # side stated but no code for it: stay at the parent
    parent = tree()[next(iter(codes.values()))]
    return (parent, 0.4) if parent else (None, 0.0)  # side unknown: never guess


def _quadrant_or_jaw(codes: list[str]) -> str | None:
    """Nearest shared tree ancestor of several teeth, only within a jaw."""
    chains = []
    for c in codes:
        chain = [c]
        while tree()[chain[-1]]:
            chain.append(tree()[chain[-1]])
        chains.append(chain)
    for anc in chains[0][1:]:
        if anc in ("jaw_upper", "jaw_lower", *(f"quadrant_{i}" for i in range(1, 9))) and all(
            anc in ch for ch in chains
        ):
            return anc
    return None


def map_region(text: str, unit: str | None = None) -> tuple[str | None, float]:
    """Best region_code for a location string, with a 0-1 confidence; (None, 0.0) if unsure.

    `unit` ("dental", ...) only enables bare tooth numbers like "36, 37".
    """
    try:
        teeth = parse_fdi(text, dental_context=unit == "dental")
    except InvalidFdi:
        return None, 0.0
    if len(teeth) == 1:
        return f"tooth_{teeth[0]}", 0.98
    if teeth:
        code = _quadrant_or_jaw([f"tooth_{n}" for n in teeth])
        return (code, 0.7) if code else (None, 0.0)

    t = normalize(text)
    hits = []  # (concept index, term length)
    for i, (terms, _) in enumerate(concepts()):
        for term in terms:
            m = re.search(rf"\b{re.escape(term)}s?\b", t)
            if m:
                hits.append((len(term), m.span(), i))
    hits.sort(key=lambda h: -h[0])
    seen: set[int] = set()
    used: list[tuple[int, int]] = []
    for _, (a, b), i in hits:  # longest phrase wins; shorter ones inside it are masked
        if any(a < ub and ua < b for ua, ub in used):
            continue
        used.append((a, b))
        seen.add(i)
    if len(seen) != 1:  # nothing found, or several regions mentioned: do not pick one
        return None, 0.0
    return _resolve(concepts()[seen.pop()][1], _side(t))
