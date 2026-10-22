import json
from collections import Counter
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from synth_gen import generate

SCHEMAS = Path(__file__).resolve().parents[3] / "eval" / "golden-v0" / "schemas"
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
