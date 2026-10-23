"""Odontogram SVG: one <g id=tooth_NN> per permanent FDI tooth in the region tree, 5 surface shapes each.

Surface ids (`<tooth>__M|D|O|B|L`) are viewer-level, not region_codes.
"""

import re
import xml.etree.ElementTree as ET  # trusted, repo-owned file
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "data/terminology/region-tree.v1.yaml"
SVG = ROOT / "packages/anatomy-assets/svg/odontogram.svg"
SURFACES = ("M", "D", "O", "B", "L")


def test_odontogram_has_every_permanent_tooth_with_five_surfaces():
    nodes = yaml.safe_load(TREE.read_text(encoding="utf-8"))
    teeth = {r["region_code"] for r in nodes if re.fullmatch(r"tooth_[1-4][1-8]", r["region_code"])}
    assert len(teeth) == 32
    root = ET.parse(SVG).getroot()  # noqa: S314
    ids = [e.get("id") for e in root.iter() if e.get("id") and e.get("id") != "odo-t"]
    assert len(ids) == len(set(ids)), "duplicate ids"
    expected = teeth | {f"{t}__{s}" for t in teeth for s in SURFACES}
    assert set(ids) == expected, f"unknown {set(ids) - expected}, missing {expected - set(ids)}"
    for g in root.iter("{*}g"):
        if g.get("id") in teeth:
            kids = {k.get("id") for k in g if k.get("id")}
            assert kids == {f"{g.get('id')}__{s}" for s in SURFACES}
            assert g.find("{*}title") is not None and g.find("{*}text") is not None


def test_odontogram_is_inert():
    for e in ET.parse(SVG).getroot().iter():  # noqa: S314
        assert e.tag.split("}")[-1] not in ("script", "image", "foreignObject")
        assert not any(k.lower().startswith("on") or k.endswith("href") for k in e.attrib)
