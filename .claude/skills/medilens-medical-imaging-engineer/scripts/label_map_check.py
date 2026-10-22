#!/usr/bin/env python3
"""Validate a segmentation-label → region_code map.

Usage: python label_map_check.py label-map.csv regions.csv

label-map.csv columns: ts_label, region_code, laterality
regions.csv columns: region_code[, laterality]
Checks: unknown region codes, duplicate labels, two labels mapped to the same
region (warning), left/right words in the label vs laterality column and vs the
region code suffix (_l/_r). Exit 1 on errors.
"""

import csv
import sys


def side_from_label(label):
    l = label.lower()
    if "left" in l.split("_") or l.endswith("_left"):
        return "left"
    if "right" in l.split("_") or l.endswith("_right"):
        return "right"
    return None


def side_from_region(code):
    parts = code.lower().split("_")
    if "l" in parts[1:]:
        return "left"
    if "r" in parts[1:]:
        return "right"
    return None


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    regions = {}
    with open(argv[2], newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            regions[r["region_code"].strip()] = (r.get("laterality") or "").strip()
    errors, warns, seen, used = [], [], set(), {}
    with open(argv[1], newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), 2):
            label, code = r["ts_label"].strip(), r["region_code"].strip()
            lat = (r.get("laterality") or "").strip().lower()
            if label in seen:
                errors.append(f"line {i}: duplicate label {label}")
            seen.add(label)
            if code not in regions:
                errors.append(f"line {i}: region_code {code} not in region list")
            used.setdefault(code, []).append(label)
            ls, rs = side_from_label(label), side_from_region(code)
            if ls and lat and ls != lat:
                errors.append(f"line {i}: label {label} is {ls} but laterality column says {lat}")
            if ls and rs and ls != rs:
                errors.append(f"line {i}: label {label} is {ls} but region {code} is {rs}")
            if code in regions and regions[code] and lat and regions[code].lower() != lat:
                warns.append(
                    f"line {i}: laterality {lat} differs from region list ({regions[code]})"
                )
    for code, labels in used.items():
        if len(labels) > 1:
            warns.append(
                f"region {code} receives several labels: {', '.join(labels)} (merge meshes?)"
            )
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"labels={len(seen)} → {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
