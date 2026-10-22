#!/usr/bin/env python3
"""Validate a MediLens License Register CSV.

Usage: python license_register_check.py license-register.csv [--commercial] [--today YYYY-MM-DD]

Errors (exit 1): missing columns, duplicate lic_id, empty decision or pending
decision for a source with intended use, training/product use marked as
intended while the register says not allowed, NC sources approved for product
use when --commercial is set, next_review in the past.
Warnings: share-alike sources, unclear rights, missing attribution for CC BY*.
"""

import csv
import sys
from datetime import date

REQUIRED = [
    "lic_id",
    "source_name",
    "licence_name",
    "training_allowed",
    "product_use_allowed",
    "commercial_allowed",
    "share_alike",
    "intended_use",
    "decision",
    "reviewer",
    "next_review",
]


def yes(v):
    return (v or "").strip().lower() in ("yes", "y", "true", "1")


def main(argv):
    args = argv[1:]
    if not args:
        print(__doc__)
        return 2
    commercial = "--commercial" in args
    today = date.today()
    if "--today" in args:
        today = date.fromisoformat(args[args.index("--today") + 1])
    path = [a for a in args if not a.startswith("--") and not a[:4].isdigit()][0]
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print("empty register")
        return 1
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        print("Missing columns:", ", ".join(missing))
        return 1
    errors, warns, seen = [], [], set()
    for r in rows:
        lid = r["lic_id"].strip()
        if lid in seen:
            errors.append(f"{lid}: duplicate id")
        seen.add(lid)
        decision = (r.get("decision") or "").strip().lower()
        use = (r.get("intended_use") or "").lower()
        lic = (r.get("licence_name") or "").upper()
        if not decision or decision == "pending":
            errors.append(f"{lid}: no decision — do not download/use")
            continue
        if decision == "rejected":
            continue
        if "train" in use and not yes(r.get("training_allowed")):
            errors.append(f"{lid}: intended use includes training but training_allowed is not yes")
        if ("product" in use or "commercial" in use) and not yes(r.get("product_use_allowed")):
            errors.append(f"{lid}: intended product use but product_use_allowed is not yes")
        if (
            commercial
            and ("-NC" in lic or "NC-" in lic or "NONCOMMERCIAL" in lic.replace(" ", ""))
            and ("product" in use or "commercial" in use or "train" in use)
        ):
            errors.append(
                f"{lid}: non-commercial licence used for product/training in commercial mode"
            )
        if commercial and "DUA" in (r.get("notes", "") + lic).upper() and "product" in use:
            errors.append(f"{lid}: DUA-restricted source marked for product use")
        for col in ("training_allowed", "product_use_allowed", "commercial_allowed"):
            if (r.get(col) or "").strip().lower() in ("", "unclear", "unknown"):
                warns.append(f"{lid}: {col} unclear — ask Regulatory")
        if yes(r.get("share_alike")):
            warns.append(f"{lid}: share-alike — derived data/assets must keep the same licence")
        if lic.startswith("CC BY") and not (r.get("attribution_text") or "").strip():
            warns.append(f"{lid}: CC BY licence without attribution text")
        nr = (r.get("next_review") or "").strip()
        if nr:
            try:
                if date.fromisoformat(nr) < today:
                    errors.append(f"{lid}: review overdue since {nr}")
            except ValueError:
                errors.append(f"{lid}: next_review is not a date ({nr})")
        else:
            errors.append(f"{lid}: next_review missing")
    print(
        f"Sources: {len(rows)}  mode: {'commercial' if commercial else 'learning'}  today: {today}"
    )
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("RESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
