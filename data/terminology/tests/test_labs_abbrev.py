import csv
from pathlib import Path

import yaml
from loaders._codecheck import check_code

HERE = Path(__file__).resolve().parents[1]


def _labs():
    with (HERE / "loinc-labs.v1.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_loinc_codes_valid_and_unique():
    rows = _labs()
    codes = [r["loinc_num"] for r in rows]
    assert len(codes) == len(set(codes)) >= 30
    assert [c for c in codes if check_code("LOINC", c)] == []
    assert all(r["long_common_name"] and r["ucum_unit"] and r["aliases"] for r in rows)


def test_abbreviations_shape():
    rows = yaml.safe_load((HERE / "abbreviations.v1.yaml").read_text(encoding="utf-8"))
    assert len({r["abbr"].lower() for r in rows}) == len(rows)
    for r in rows:
        assert set(r) == {"abbr", "expansions"} and r["expansions"]
        assert all(set(e) == {"vi", "en"} and e["vi"] and e["en"] for e in r["expansions"])
