import csv
from pathlib import Path

import pytest
import yaml
from loaders import fdi

ROOT = Path(__file__).resolve().parents[1]
LATERALITY = {"left", "right", "bilateral", "midline", "unknown"}


@pytest.fixture(scope="module")
def tree():
    return yaml.safe_load((ROOT / "region-tree.v1.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_code(tree):
    return {r["region_code"]: r for r in tree}


def test_ids_unique(tree):
    codes = [r["region_code"] for r in tree]
    assert len(codes) == len(set(codes))


def test_required_fields_and_snomed_empty(tree):
    for r in tree:
        for k in ("name_vi", "name_en", "laterality", "svg_id", "mesh_id", "std_code"):
            assert k in r, (r["region_code"], k)
        assert r["name_vi"] and r["name_en"]
        assert r["std_code"] == "", "SNOMED is not licensed; std_code must stay empty"


def test_single_root_and_parents_exist(tree, by_code):
    roots = [r for r in tree if r["parent"] is None]
    assert [r["region_code"] for r in roots] == ["body"]
    for r in tree:
        assert r["parent"] is None or r["parent"] in by_code, r["region_code"]


def test_no_cycles(tree, by_code):
    for r in tree:
        seen, cur = set(), r
        while cur["parent"] is not None:
            assert cur["region_code"] not in seen
            seen.add(cur["region_code"])
            cur = by_code[cur["parent"]]


def test_laterality_consistent(tree, by_code):
    for r in tree:
        code, lat = r["region_code"], r["laterality"]
        assert lat in LATERALITY, code
        if code.endswith("_r"):
            assert lat == "right", code
        if code.endswith("_l"):
            assert lat == "left", code
        parent = by_code.get(r["parent"])
        if parent and parent["laterality"] in ("left", "right"):
            assert lat == parent["laterality"], f"{code} contradicts parent side"


def test_fdi_csv_matches_generator():
    with (ROOT / "fdi.csv").open(encoding="utf-8") as fh:
        assert list(csv.DictReader(fh)) == fdi.rows()


def test_fdi_has_52_teeth():
    rows = fdi.rows()
    assert len(rows) == 52
    assert sum(r["dentition"] == "permanent" for r in rows) == 32


def test_every_fdi_tooth_in_tree(by_code):
    for r in fdi.rows():
        node = by_code.get(f"tooth_{r['fdi']}")
        assert node, r["fdi"]
        assert node["parent"] == f"quadrant_{r['quadrant']}"
        assert node["laterality"] == r["laterality"]
        assert by_code[node["parent"]]["parent"] == f"jaw_{r['arch']}"


def test_no_unknown_teeth_in_tree(tree):
    teeth = {
        r["region_code"].removeprefix("tooth_")
        for r in tree
        if r["region_code"].startswith("tooth_")
    }
    assert teeth == {r["fdi"] for r in fdi.rows()}


@pytest.mark.parametrize(
    "code",
    [
        "heart_ra", "heart_la", "heart_rv", "heart_lv",
        "valve_aortic", "valve_mitral", "valve_tricuspid", "valve_pulmonary",
        "cor_rca", "cor_lmca", "cor_lad", "cor_lcx", "aorta", "pulmonary_trunk",
        "ln_mediastinal", "ln_axillary_r", "ln_axillary_l", "bone_spine",
    ],
)  # fmt: skip
def test_cardiology_oncology_core_present(by_code, code):
    assert code in by_code


@pytest.mark.parametrize("organ", ["liver", "brain", "bone_sites"])
def test_common_metastatic_sites_flagged(by_code, organ):
    assert by_code[organ]["metastatic_site"] is True


def test_paired_sites_have_both_sides(by_code):
    for code in list(by_code):
        if code.endswith("_r") and not code.startswith("tooth_"):
            assert code[:-2] + "_l" in by_code, code
