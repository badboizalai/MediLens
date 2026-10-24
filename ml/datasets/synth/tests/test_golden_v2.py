import csv
import json
import re
from collections import Counter
from pathlib import Path

import pytest
from synth_gen import golden_v2
from test_generate import _validators

ML = Path(__file__).resolve().parents[3]
TERM = ML.parent / "data" / "terminology"
COMMITTED = ML / "eval" / "golden-v2"
FORBIDDEN = re.compile(r"prognos|survival|tiên lượng|sống (còn|thêm)|\b[A-TV-Z]\d{2}(\.\d{1,2})?\b")


@pytest.fixture(scope="module")
def built():
    return golden_v2.build()


@pytest.fixture(scope="module")
def gold(built):
    return [json.loads(x) for x in built["gold.jsonl"].splitlines()]


def _walk(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(o, list):
        for i in o:
            yield from _walk(i, key)


def test_200_per_unit_and_unique_ids(gold):
    assert Counter(r["unit"] for r in gold) == {"dental": 200, "cardiology": 200, "oncology": 200}
    assert len({r["doc_id"] for r in gold}) == 600


def test_gold_validates_against_schemas(gold):
    v = _validators()
    for r in gold:
        errs = list(v[r["unit"]].iter_errors(r["fields"]))
        assert not errs, (r["doc_id"], errs[:1])


def test_strata_coverage_per_unit(gold):
    for unit in ("dental", "cardiology", "oncology"):
        rs = [r["strata"] for r in gold if r["unit"] == unit]
        assert Counter(s["lang"] for s in rs) == {"vi": 140, "en": 60}
        assert Counter(s["noise"] for s in rs) == {"clean": 100, "light": 70, "heavy": 30}
        assert {s["layout"] for s in rs} == set(golden_v2.LAYOUTS[unit])
        assert len({(s["lang"], s["noise"]) for s in rs}) == 6  # every lang x noise cell


def test_region_codes_and_loinc_exist_in_terminology(gold):
    tree = (TERM / "region-tree.v1.yaml").read_text(encoding="utf-8")
    codes = set(re.findall(r"region_code: (\S+)", tree))
    loinc = set()
    for f in ("loinc-cardiology.v1.csv", "loinc-labs.v1.csv"):
        with (TERM / f).open(encoding="utf-8") as fh:
            loinc |= {row["loinc_num"] for row in csv.DictReader(fh)}
    for r in gold:
        for reg in _walk(r["fields"], "region"):
            assert reg["region_code"] is None or reg["region_code"] in codes, r["doc_id"]
        for hint in _walk(r["fields"], "loinc_hint"):
            assert hint in loinc, (r["doc_id"], hint)


def test_oncology_covers_tnm_nodes_metastases(gold):
    onc = [r["fields"] for r in gold if r["unit"] == "oncology"]
    assert all({"t", "n", "m"} <= set(f["tnm"]) and f["primary"]["region"] for f in onc)
    assert any(f["nodes"] for f in onc) and any(f["metastases"] for f in onc)
    assert any(n["involved"] is False for f in onc for n in f["nodes"])
    assert all(f["metastases"] == [] for f in onc if f["tnm"]["m"]["value"] == "M0")


def test_no_icd10_prognosis_or_real_identity(built):
    for name in ("gold.jsonl", "docs.jsonl"):
        assert not FORBIDDEN.search(built[name]), name
    for line in built["docs.jsonl"].splitlines():
        d = json.loads(line)
        assert 1900 <= d["patient"]["birth_year"] <= 1950
        assert d["patient"]["name"].split()[0] in golden_v2.content.FAMILY
        assert "SYNTHETIC" in d["text_clean"]


def test_noise_damages_text_only_when_requested(built):
    docs = [json.loads(x) for x in built["docs.jsonl"].splitlines()]
    assert all(d["text"] == d["text_clean"] for d in docs if d["strata"]["noise"] == "clean")
    assert any(d["text"] != d["text_clean"] for d in docs if d["strata"]["noise"] == "heavy")


def test_deterministic_and_seed_sensitive(built):
    assert golden_v2.build() == built
    assert golden_v2.build(seed=1)["gold.jsonl"] != built["gold.jsonl"]


def test_committed_files_are_up_to_date(built):
    for name, text in built.items():
        assert (COMMITTED / name).read_text(encoding="utf-8") == text, name
