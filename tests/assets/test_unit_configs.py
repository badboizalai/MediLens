"""Unit configs: schema-valid, regions in the region tree, LOINC codes in the subset with matching UCUM unit."""

import copy
import csv
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
UNITS = ROOT / "packages/anatomy-assets/units"
SCHEMA = json.loads((UNITS / "unit-config.schema.json").read_text(encoding="utf-8"))
TREE = yaml.safe_load((ROOT / "data/terminology/region-tree.v1.yaml").read_text(encoding="utf-8"))
REGIONS = {r["region_code"] for r in TREE}
with (ROOT / "data/terminology/loinc-cardiology.v1.csv").open(encoding="utf-8") as f:
    LOINC = {r["loinc_num"]: r["ucum_unit"] or None for r in csv.DictReader(f)}


def load(name):
    return yaml.safe_load((UNITS / f"{name}.yaml").read_text(encoding="utf-8"))


def problems(cfg):
    out = [e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(cfg)]
    out += [f"region {r}" for r in cfg["regions"] if r not in REGIONS]
    for o in cfg.get("observations", []):
        if o["region"] not in cfg["regions"]:
            out.append(f"obs region {o['region']}")
        if o["loinc"] not in LOINC:
            out.append(f"loinc {o['loinc']}")
        elif LOINC[o["loinc"]] != o["unit"]:
            out.append(f"unit {o['loinc']}")
    if not (ROOT / cfg["extraction_schema"]).is_file():
        out.append("extraction_schema")
    return out


@pytest.mark.parametrize("name", ["dental", "cardiology"])
def test_unit_config_is_valid(name):
    cfg = load(name)
    assert cfg["unit_code"] == name
    assert problems(cfg) == []


def test_cardiology_loinc_codes():
    got = {o["key"]: o["loinc"] for o in load("cardiology")["observations"]}
    assert got == {
        "lvef": "10230-1",
        "bp_systolic": "8480-6",
        "bp_diastolic": "8462-4",
        "bp_panel": "85354-9",
    }


def test_bad_codes_are_caught():
    bad = copy.deepcopy(load("cardiology"))
    bad["regions"].append("not_a_region")
    bad["observations"][0]["loinc"] = "99999-9"
    bad["observations"][1]["unit"] = "%"
    assert {"region not_a_region", "loinc 99999-9", "unit 8480-6"} <= set(problems(bad))
