from pathlib import Path

import pytest
import yaml
from loaders.base import InvalidCodeFile
from loaders.dental import load_dental_terms
from loaders.licence import LicenceNotApproved

TERMS = Path(__file__).resolve().parents[1] / "dental-terms.v1.yaml"


def _write(tmp_path, rows):
    p = tmp_path / "t.yaml"
    p.write_text(yaml.safe_dump(rows, allow_unicode=True), encoding="utf-8")
    return p


def test_shipped_file_valid_and_sized():
    assert 40 <= len(load_dental_terms()) <= 80


def test_no_icd_data_shipped():
    assert all(not r["icd10"] for r in load_dental_terms())


def test_no_diagnosis_wording():
    text = TERMS.read_text(encoding="utf-8").lower()
    assert "chẩn đoán" not in text and "prognosis" not in text and "dose" not in text


def test_duplicate_id_rejected(tmp_path):
    row = {"term_id": "dt_a", "vi": "a", "en": "a"}
    with pytest.raises(InvalidCodeFile, match="duplicate"):
        load_dental_terms(_write(tmp_path, [row, row]))


def test_empty_vi_rejected(tmp_path):
    with pytest.raises(InvalidCodeFile, match="empty"):
        load_dental_terms(_write(tmp_path, [{"term_id": "dt_a", "vi": " ", "en": "a"}]))


def test_unknown_region_rejected(tmp_path):
    row = {"term_id": "dt_a", "vi": "a", "en": "a", "region_hint": "nope"}
    with pytest.raises(InvalidCodeFile, match="region_hint"):
        load_dental_terms(_write(tmp_path, [row]))


def test_icd10_refused_while_licence_unapproved(tmp_path):
    row = {"term_id": "dt_a", "vi": "a", "en": "a", "icd10": "K02"}
    with pytest.raises(LicenceNotApproved):
        load_dental_terms(_write(tmp_path, [row]))
