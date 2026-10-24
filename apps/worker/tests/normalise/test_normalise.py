import pytest
from medilens_worker.normalise import expand_abbreviation, to_icd10, to_loinc
from medilens_worker.normalise.icd import LicenceNotApproved


def _en(text):
    return {e.en for e in expand_abbreviation(text)}


def test_unambiguous_abbreviation_expands_vi_and_en():
    (e,) = expand_abbreviation("NMCT")
    assert (e.vi, e.en) == ("nhồi máu cơ tim", "myocardial infarction")


@pytest.mark.parametrize("text", ["nmct", "N.M.C.T", " NMCT. ", "ĐTĐ", "dtd", "HbA1C"])
def test_case_diacritics_punctuation_insensitive(text):
    assert len(expand_abbreviation(text)) == 1


@pytest.mark.parametrize(
    "text,n", [("THA", 2), ("MI", 2), ("HR", 2), ("RA", 3), ("CA", 2), ("TB", 2)]
)
def test_ambiguous_returns_all_candidates_never_one(text, n):
    assert len(expand_abbreviation(text)) == n


def test_ambiguous_includes_both_meanings():
    assert {"hypertension", "total hip arthroplasty"} <= _en("THA")


def test_unknown_returns_empty():
    assert expand_abbreviation("zzqx") == []
    assert expand_abbreviation("") == []


def test_dental_abbrev_wired_in():
    (e,) = expand_abbreviation("VNC")
    assert e.vi == "viêm nha chu"
    assert "periodontitis" in e.en


def test_lab_exact_vi_and_en():
    m = to_loinc("Creatinine", unit="mg/dL")
    assert (m.code, m.confidence) == ("2160-0", 1.0)
    assert to_loinc("tiểu cầu", unit="G/L").code == "777-3"  # 10^9/L == 10*3/uL
    assert to_loinc("tiểu cầu").code == "777-3"


def test_unit_selects_between_same_analyte():
    assert to_loinc("Glucose", unit="mg/dL").code == "2345-7"
    assert to_loinc("Glucose", unit="mmol/L").code == "15074-8"


def test_unit_inside_text_and_value_ignored():
    assert to_loinc("Glucose máu 5.6 mmol/L").code == "15074-8"
    assert to_loinc("LDL-C 3.1mmol/L").code == "22748-8"
    assert to_loinc("SpO2: 98%").code == "59408-5"
    assert to_loinc("WBC 7.2 K/uL").code == "6690-2"


def test_missing_unit_for_multi_unit_analyte_is_ambiguous():
    assert to_loinc("Glucose") is None


def test_wrong_unit_refused():
    assert to_loinc("Glucose", unit="kg") is None


def test_token_order_and_punctuation():
    assert to_loinc("cholesterol HDL", unit="mg/dl").code == "2085-9"
    assert to_loinc("NT-proBNP", unit="pg/mL").code == "33762-6"


def test_typo_matched_by_fuzzy_with_lower_confidence():
    m = to_loinc("Triglycerides", unit="mg/dL")
    t = to_loinc("Triglicerides", unit="mg/dL")
    assert t.code == m.code == "2571-8"
    assert 0.85 <= t.confidence < 1.0


def test_troponin_without_type_is_ambiguous():
    assert to_loinc("Troponin", unit="ng/L") is None
    assert to_loinc("Troponin hs", unit="ng/L") is None  # 'hs' must not be fuzzed into 'T'


def test_short_alias_never_fuzzy():
    assert to_loinc("AXT", unit="U/L") is None


@pytest.mark.parametrize("text", ["", "   ", "xin chao", "bệnh nhân ổn", "120/80"])
def test_garbage_returns_none(text):
    assert to_loinc(text) is None


def test_icd_path_refused_while_licence_gate_closed():
    with pytest.raises(LicenceNotApproved):
        to_icd10("viêm nha chu")


def test_icd_path_loads_nothing_even_if_gate_opens(tmp_path):
    reg = tmp_path / "r.csv"
    reg.write_text("lic_id,source_name,decision\nLIC-002,x,approved\n", encoding="utf-8")
    with pytest.raises(NotImplementedError):
        to_icd10("viêm nha chu", register=reg)
