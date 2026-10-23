import json
from collections import Counter
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from synth_gen import generate, render

SCHEMAS = Path(__file__).resolve().parents[3] / "schemas"
FDI = {f"{q}{n}" for q in (1, 2, 3, 4) for n in range(1, 9)}


def _validators():
    docs = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in SCHEMAS.glob("*.json")}
    reg = Registry().with_resources(
        (d["$id"], Resource.from_contents(d)) for d in docs.values() if "$id" in d
    )
    return {
        u: Draft202012Validator(docs[f"{u}.v1"], registry=reg)
        for u in ("dental", "cardiology", "oncology")
    }


@pytest.fixture(scope="module")
def records(tmp_path_factory):
    return generate.generate(tmp_path_factory.mktemp("g"), images=False)


def test_every_record_matches_unit_schema(records):
    validators = _validators()
    for r in records:
        errs = list(validators[r["unit"]].iter_errors(r["fields"]))
        assert not errs, (r["doc_id"], errs[:1])


def test_unit_distribution(records):
    c = Counter(r["unit"] for r in records)
    assert len(records) == 50
    assert c == {"dental": 17, "cardiology": 17, "oncology": 16}
    langs = Counter(r["metadata"]["lang"] for r in records)
    assert langs["vi"] > langs["en"] > 0


def test_deterministic(tmp_path):
    a = generate.generate(tmp_path / "a", seed=7, images=False)
    b = generate.generate(tmp_path / "b", seed=7, images=False)
    c = generate.generate(tmp_path / "c", seed=8, images=False)
    assert a == b
    assert a != c


def test_images_deterministic_and_small(tmp_path):
    generate.generate(tmp_path / "a")
    generate.generate(tmp_path / "b")
    files = sorted((tmp_path / "a" / "images").glob("*.jpg"))
    assert len(files) > 50  # clean for all + degraded variants
    for f in files:
        assert f.read_bytes() == (tmp_path / "b" / "images" / f.name).read_bytes()
    assert sum(f.stat().st_size for f in files) < 25 * 1024 * 1024


def test_synthetic_safety_and_plausibility(records):
    for r in records:
        m = r["metadata"]
        assert m["synthetic"] is True
        assert 1900 <= m["patient"]["birth_year"] <= 1950
        if r["unit"] == "dental":
            assert all(t["fdi"]["value"] in FDI for t in r["fields"]["teeth"])
        if r["unit"] == "oncology":
            m_stage = r["fields"]["tnm"]["m"]["value"]
            assert bool(r["fields"]["metastases"]) == (m_stage == "M1")
        text = json.dumps(r, ensure_ascii=False).lower()
        assert "mg " not in text and "liều" not in text and "dose" not in text


def test_perspective_and_handwriting_subset(tmp_path):
    recs = generate.generate(tmp_path)
    kinds = Counter(
        im["variant"]
        for r in recs
        for im in r["metadata"]["images"]
        if im["variant"] in ("handwriting", "perspective")
    )
    assert kinds == {"handwriting": 5, "perspective": 5}  # 20 % of 50 records
    for r in recs:
        for im in r["metadata"]["images"]:
            if im["variant"] == "perspective":
                assert im["degradations"][0]["type"] == "perspective"
                assert len(im["degradations"][0]["corners"]) == 4
            if im["variant"] == "handwriting":
                clean = (tmp_path / im["file"].replace("handwriting", "clean")).read_bytes()
                assert (tmp_path / im["file"]).read_bytes() != clean


def test_ground_truth_unchanged_by_variants(tmp_path):
    with_img = generate.generate(tmp_path)
    no_img = generate.generate(tmp_path / "n", images=False)
    assert [r["fields"] for r in with_img] == [r["fields"] for r in no_img]


def test_perspective_coeffs_identity():
    pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
    c = render._perspective_coeffs(pts, pts)
    assert [round(v, 6) for v in c] == [1, 0, 0, 0, 1, 0, 0, 0]


@pytest.fixture(scope="module")
def records_v1(tmp_path_factory):
    return generate.generate(
        tmp_path_factory.mktemp("g1"), generate.V1_SEED, images=False, profile="v1"
    )


def test_v1_150_docs_schema_valid_with_regions(records_v1):
    validators = _validators()
    assert len(records_v1) == 150
    assert Counter(r["unit"] for r in records_v1) == {
        "dental": 50,
        "cardiology": 50,
        "oncology": 50,
    }
    assert Counter(r["quality"] for r in records_v1) == {"good": 75, "medium": 53, "poor": 22}
    assert len({r["doc_id"] for r in records_v1}) == 150
    for r in records_v1:
        assert r["doc_id"].startswith("gv1-")
        errs = list(validators[r["unit"]].iter_errors(r["fields"]))
        assert not errs, (r["doc_id"], errs[:1])
        if r["unit"] == "dental":
            for t in r["fields"]["teeth"]:
                assert t["region"]["region_code"] == f"tooth_{t['fdi']['value']}"


def test_schema_rejects_missing_source():
    bad = {
        "encounter": {},
        "teeth": [{"fdi": {"value": "11", "confidence": 1}, "condition": "caries"}],
    }
    assert list(_validators()["dental"].iter_errors(bad))


def test_v1_variants_20_percent_and_size(tmp_path):
    recs = generate.generate(tmp_path, generate.V1_SEED, profile="v1")
    kinds = Counter(
        im["variant"]
        for r in recs
        for im in r["metadata"]["images"]
        if im["variant"] in ("handwriting", "perspective")
    )
    assert kinds == {"handwriting": 15, "perspective": 15}
    size = sum(f.stat().st_size for f in (tmp_path / "images").glob("*.jpg"))
    assert size < 30 * 1024 * 1024
