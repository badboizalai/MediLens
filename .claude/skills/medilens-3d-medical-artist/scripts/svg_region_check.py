#!/usr/bin/env python3
"""Check SVG region ids against the MediLens region list.

Usage: python svg_region_check.py body.svg --regions regions.csv [--column svg_required]

Finds every element id in the SVG (standard library XML parser), reports
duplicate ids, ids that are not region codes (ignoring 'sys_' groups and ids
starting with 'aux_' or 'defs_'), regions required in 2D that are missing, and
forbidden content (script elements, external hrefs, inline fill on regions).
Exit 1 on errors.
"""

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET

SURFACE_RX = re.compile(r"^(tooth_\d{2})_[OMDBL]$")


def local(tag):
    return tag.split("}")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("--regions", required=True)
    ap.add_argument("--column", default="svg_required")
    a = ap.parse_args()
    with open(a.regions, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    allowed = {r["region_code"] for r in rows}
    required = {r["region_code"] for r in rows if (r.get(a.column) or "yes").lower() == "yes"}
    tree = ET.parse(a.svg)
    ids, errors, warns = [], [], []
    for el in tree.iter():
        tag = local(el.tag)
        if tag == "script":
            errors.append("contains <script>")
        for k, v in el.attrib.items():
            if local(k) == "href" and not v.startswith("#"):
                errors.append(f"external reference {v}")
        i = el.attrib.get("id")
        if i:
            ids.append(i)
            if (
                tag in ("path", "polygon", "ellipse", "circle", "rect")
                and "fill" in el.attrib
                and not i.startswith("aux_")
            ):
                warns.append(f"region '{i}' has inline fill (viewer should set colours)")
    seen, dup = set(), set()
    for i in ids:
        if i in seen:
            dup.add(i)
        seen.add(i)
    for d in sorted(dup):
        errors.append(f"duplicate id '{d}'")
    present = set()
    for i in seen:
        if i.startswith(("sys_", "aux_", "defs_")):
            continue
        m = SURFACE_RX.match(i)
        base = m.group(1) if m else i
        if base not in allowed:
            errors.append(f"id '{i}' is not a region_code")
        present.add(base)
    for code in sorted(required - present):
        if code.startswith("sys_"):
            continue
        errors.append(f"required region '{code}' missing in SVG")
    print(f"{a.svg}: {len(seen)} ids")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("RESULT:", "FAIL" if errors else "PASS")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
