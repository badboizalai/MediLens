#!/usr/bin/env python3
"""Validate a MediLens hazard log CSV.

Usage: python hazard_risk_check.py hazard-log.csv [--strict]

Accepts the project columns of safety/hazard-log.csv (id, hazard, cause, likelihood,
residual_likelihood) or the older names via an alias map; cs_ids are taken from
CS-nnn references in controls when that column is absent.

Checks each row for: required fields, S/P in 1..5, controls and CS links present,
residual risk region (acceptable 1-4, ALARP 5-9, unacceptable >= 10), severity-5
residuals needing explicit sign-off, and information-only controls for S >= 4.
Exit code 1 when any blocking problem is found (unacceptable residual, missing
controls or CS links); --strict also fails on ALARP rows without notes.
"""

import csv
import re
import sys

# Project hazard-log column names -> canonical (template) names.
ALIASES = {
    "id": "hazard_id",
    "hazard": "title",
    "cause": "causes",
    "likelihood": "probability",
    "residual_likelihood": "residual_probability",
}
CS_REF = re.compile(r"CS-\d+")

REQUIRED = [
    "hazard_id",
    "title",
    "harm",
    "severity",
    "probability",
    "controls",
    "cs_ids",
    "residual_severity",
    "residual_probability",
    "owner",
    "status",
]
INFO_ONLY_WORDS = ("disclaimer", "label", "warning text", "help text", "banner")


def normalize(row):
    """Map project column names to canonical ones; derive cs_ids from controls."""
    out = dict(row)
    for alias, canon in ALIASES.items():
        if alias in out and not (out.get(canon) or "").strip():
            out[canon] = out[alias]
    if not (out.get("cs_ids") or "").strip():
        out["cs_ids"] = ";".join(dict.fromkeys(CS_REF.findall(out.get("controls") or "")))
    return out


def region(score: int) -> str:
    if score >= 10:
        return "UNACCEPTABLE"
    if score >= 5:
        return "ALARP"
    return "acceptable"


def as_int(value, field, hid, problems):
    try:
        n = int(str(value).strip())
    except ValueError:
        problems.append(f"{hid}: {field} is not a number ({value!r})")
        return None
    if not 1 <= n <= 5:
        problems.append(f"{hid}: {field} must be 1..5 (got {n})")
        return None
    return n


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    strict = "--strict" in argv
    path = [a for a in argv[1:] if not a.startswith("--")][0]
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [normalize(r) for r in csv.DictReader(fh)]
    if not rows:
        print("No rows found.")
        return 1
    missing_cols = [c for c in REQUIRED if c not in rows[0]]
    if missing_cols:
        print("Missing columns:", ", ".join(missing_cols))
        return 1

    blocking, warnings, summary = [], [], {"acceptable": 0, "ALARP": 0, "UNACCEPTABLE": 0}
    seen = set()
    for row in rows:
        hid = (row.get("hazard_id") or "?").strip()
        if hid in seen:
            blocking.append(f"{hid}: duplicate hazard_id")
        seen.add(hid)
        for col in REQUIRED:
            if not (row.get(col) or "").strip():
                (blocking if col in ("controls", "cs_ids") else warnings).append(
                    f"{hid}: empty {col}"
                )
        s = as_int(row.get("severity"), "severity", hid, blocking)
        p = as_int(row.get("probability"), "probability", hid, blocking)
        rs = as_int(row.get("residual_severity"), "residual_severity", hid, blocking)
        rp = as_int(row.get("residual_probability"), "residual_probability", hid, blocking)
        if None in (s, p, rs, rp):
            continue
        if rs > s or rp > p:
            warnings.append(f"{hid}: residual risk higher than initial — check scoring")
        reg = region(rs * rp)
        summary[reg] += 1
        if reg == "UNACCEPTABLE":
            blocking.append(f"{hid}: residual {rs}x{rp}={rs * rp} is UNACCEPTABLE")
        elif reg == "ALARP" and strict and not (row.get("notes") or "").strip():
            blocking.append(f"{hid}: ALARP residual without justification in notes")
        if rs == 5:
            warnings.append(f"{hid}: residual severity 5 — needs explicit CSO sign-off")
        controls = (row.get("controls") or "").lower()
        if s >= 4 and controls:
            parts = [c.strip() for c in controls.replace(";", ",").split(",") if c.strip()]
            if parts and all(any(w in part for w in INFO_ONLY_WORDS) for part in parts):
                blocking.append(f"{hid}: severity {s} controlled by information only")

    print(
        f"Rows: {len(rows)} | acceptable {summary['acceptable']} | ALARP {summary['ALARP']} | "
        f"UNACCEPTABLE {summary['UNACCEPTABLE']}"
    )
    for w in warnings:
        print("WARN ", w)
    for b in blocking:
        print("BLOCK", b)
    print("RESULT:", "FAIL" if blocking else "PASS")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
