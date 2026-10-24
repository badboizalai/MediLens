"""Dictionary NER: free text -> (region_code, laterality). Rules only, never guesses.

Reads data/terminology/location-synonyms.v1.yaml (dir overridable by MEDILENS_TERMINOLOGY_DIR).
shortcut: a trimmed copy of the worker's anatomy mapper (modules/apps share no code); move both
to a shared package when a third consumer appears. Teeth and parent fallback are not supported:
anything not resolved to exactly one concrete region is unmapped.
"""

import os
import re
from functools import lru_cache
from pathlib import Path

import yaml

from medilens.modules.clinical.domain.models import norm

_DIR = Path(
    os.environ.get(
        "MEDILENS_TERMINOLOGY_DIR", Path(__file__).resolve().parents[7] / "data" / "terminology"
    )
)
_SIDE = {
    "left": re.compile(r"\b(?:trai|left)\b"),
    "right": re.compile(r"\b(?:phai|right)\b"),
}
# Group nodes colour every child (HZ-002, BR-015): never a target.
_GROUPS = {"body", "organs", "lymph_nodes", "bone_sites"}


@lru_cache(maxsize=1)
def _concepts() -> list[tuple[list[str], dict[str, str]]]:
    rows = yaml.safe_load((_DIR / "location-synonyms.v1.yaml").read_text("utf-8"))
    return [
        ([norm(t) for t in r["terms"]], {k: r[k] for k in ("code", "right", "left") if k in r})
        for r in rows
    ]


def locate(text: str) -> tuple[str | None, str | None]:
    t = norm(text)
    spans: list[tuple[int, int, int]] = []
    for i, (terms, _) in enumerate(_concepts()):
        for term in terms:
            m = re.search(rf"\b{re.escape(term)}s?\b", t)
            if m:
                spans.append((m.start(), m.end(), i))
    spans.sort(key=lambda s: s[0] - s[1])  # longest phrase first; shorter ones inside it are masked
    kept: list[tuple[int, int, int]] = []
    for a, b, i in spans:
        if not any(a < kb and ka < b for ka, kb, _ in kept):
            kept.append((a, b, i))
    if len({i for _, _, i in kept}) != 1:
        return None, None  # nothing, or several regions mentioned
    codes = _concepts()[kept[0][2]][1]
    sides = {s for s, rx in _SIDE.items() if rx.search(t)}
    side = sides.pop() if len(sides) == 1 else None
    if side in codes:
        return codes[side], side
    code = codes.get("code")
    return (code, side) if code and code not in _GROUPS else (None, None)
