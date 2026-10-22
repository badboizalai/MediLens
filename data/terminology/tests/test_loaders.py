import csv
import shutil
from pathlib import Path

import pytest
from loaders import InvalidCodeFile, LicenceNotApproved, load_icd10, load_loinc
from loaders.licence import REGISTER

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def approved_register(tmp_path):
    """Copy of the real register with LIC-002/003 flipped to approved (test only)."""
    with REGISTER.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fields = reader.fieldnames
    for r in rows:
        if r["lic_id"] in ("LIC-002", "LIC-003"):
            r["decision"] = "approved"
    out = tmp_path / "register.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return out


def test_real_register_refuses_icd10():
    with pytest.raises(LicenceNotApproved, match="LIC-002.*needs-verification"):
        load_icd10(FIX / "icd10_synth.csv")


def test_real_register_refuses_loinc():
    with pytest.raises(LicenceNotApproved, match="LIC-003.*needs-verification"):
        load_loinc(FIX / "loinc_synth.csv")


def test_refuses_before_reading_file(tmp_path):
    with pytest.raises(LicenceNotApproved):
        load_icd10(tmp_path / "does-not-exist.csv")


def test_missing_register_row(tmp_path):
    reg = tmp_path / "r.csv"
    shutil.copy(REGISTER, reg)
    reg.write_text("lic_id,source_name,decision\n")
    with pytest.raises(LicenceNotApproved, match="not found"):
        load_icd10(FIX / "icd10_synth.csv", register=reg)


def test_icd10_loads_when_approved(approved_register):
    rows = load_icd10(FIX / "icd10_synth.csv", register=approved_register)
    assert [r["code"] for r in rows] == ["A00", "B99.1"]


def test_loinc_loads_when_approved(approved_register):
    rows = load_loinc(FIX / "loinc_synth.csv", register=approved_register)
    assert [r["loinc_num"] for r in rows] == ["12345-5", "999-3"]


def test_icd10_bad_pattern(approved_register):
    with pytest.raises(InvalidCodeFile, match="line 3.*AA0"):
        load_icd10(FIX / "icd10_bad.csv", register=approved_register)


def test_loinc_bad_check_digit(approved_register):
    with pytest.raises(InvalidCodeFile, match="check digit"):
        load_loinc(FIX / "loinc_bad.csv", register=approved_register)


def test_missing_columns(approved_register):
    with pytest.raises(InvalidCodeFile, match="missing columns"):
        load_icd10(FIX / "loinc_synth.csv", register=approved_register)


def test_duplicate_code(approved_register, tmp_path):
    f = tmp_path / "dup.csv"
    f.write_text("code,title_vi\nA00,x\nA00,y\n")
    with pytest.raises(InvalidCodeFile, match="duplicate"):
        load_icd10(f, register=approved_register)
