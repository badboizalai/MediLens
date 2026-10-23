"""Every id in the body SVGs must be a region_code (or aux_/sys_); reports undrawn regions.

Run: uv run pytest tests/assets -s  (part of `make test`)
"""

import xml.etree.ElementTree as ET  # trusted, repo-owned files
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "data/terminology/region-tree.v1.yaml"
FILES = sorted((ROOT / "packages/anatomy-assets/svg").glob("body-*.svg"))


def ids(path):
    return [e.get("id") for e in ET.parse(path).iter() if e.get("id")]  # noqa: S314


def test_svg_ids_are_region_codes_with_title_and_no_external_refs():
    codes = {r["region_code"] for r in yaml.safe_load(TREE.read_text(encoding="utf-8"))}
    drawn = set()
    assert len(FILES) == 2
    for f in FILES:
        found = ids(f)
        assert len(found) == len(set(found)), f"duplicate ids in {f.name}"
        regions = [i for i in found if not i.startswith(("aux_", "sys_"))]
        assert set(regions) <= codes, f"{f.name}: unknown {set(regions) - codes}"
        root = ET.parse(f).getroot()  # noqa: S314
        for e in root.iter():
            tag = e.tag.split("}")[-1]
            assert tag not in ("script", "image", "foreignObject"), tag
            assert not any(k.endswith("href") for k in e.attrib), f.name
            if e.get("id") in regions:
                assert e.find("{*}title") is not None, f"{e.get('id')} lacks <title>"
        drawn |= set(regions)
    body = {c for c in codes if not c.startswith(("tooth_", "sys_"))}
    print(f"\ndrawn {len(drawn)}/{len(body)} non-tooth regions; undrawn: {sorted(body - drawn)}")
