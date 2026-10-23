"""Load and validate dental-terms.v1.yaml. ICD-10 stays empty until LIC-002 is approved (gate G1-D)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from ._codecheck import check_code
from .base import InvalidCodeFile
from .licence import REGISTER, require_approved

HERE = Path(__file__).resolve().parent.parent
TERMS = HERE / "dental-terms.v1.yaml"
TREE = HERE / "region-tree.v1.yaml"
ID_RE = re.compile(r"^dt_[a-z0-9_]+$")
KEYS = {"term_id", "vi", "en", "abbrev", "region_hint", "icd10"}


def load_dental_terms(
    path: Path = TERMS, tree: Path = TREE, register: Path = REGISTER
) -> list[dict]:
    rows = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    regions = {r["region_code"] for r in yaml.safe_load(Path(tree).read_text(encoding="utf-8"))}
    errors, seen = [], set()
    for r in rows:
        tid = r.get("term_id", "?")
        if set(r) - KEYS or {"term_id", "vi", "en"} - set(r):
            errors.append(f"{tid}: bad keys")
        if not ID_RE.match(str(tid)) or tid in seen:
            errors.append(f"{tid}: invalid or duplicate term_id")
        seen.add(tid)
        if not str(r.get("vi", "")).strip() or not str(r.get("en", "")).strip():
            errors.append(f"{tid}: empty vi/en")
        if r.get("region_hint") and r["region_hint"] not in regions:
            errors.append(f"{tid}: unknown region_hint '{r['region_hint']}'")
        if r.get("icd10"):  # code identifiers only, never titles; refused until LIC-002 approved
            require_approved("LIC-002", register)
            err = check_code("ICD-10", r["icd10"])
            if err:
                errors.append(f"{tid}: {err}")
    if errors:
        raise InvalidCodeFile("; ".join(errors))
    return rows
