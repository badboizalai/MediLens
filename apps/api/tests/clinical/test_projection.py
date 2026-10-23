import copy

from medilens.modules.clinical.domain.models import project

from .conftest import CARDIOLOGY, ONCOLOGY, leaf


def test_oncology_metastasis_only_when_stated_and_unmapped_region_has_no_finding() -> None:
    p = project(copy.deepcopy(ONCOLOGY), {})
    assert p is not None and p.unit_code == "oncology"
    primary, liver, bone = p.conditions
    assert primary.stage == "II" and primary.finding and primary.finding.size_mm == 22.5
    assert not primary.finding.is_metastasis
    assert liver.finding and liver.finding.is_metastasis
    assert bone.finding is None and bone.status == "suspected"  # never guess a region


def test_user_value_wins_over_model_value() -> None:
    p = project(copy.deepcopy(ONCOLOGY), {"primary.size_mm": "30", "metastases[0].site": "lung"})
    assert p and p.conditions[0].finding and p.conditions[0].finding.size_mm == 30.0
    assert p.conditions[1].label == "metastasis: lung"


def test_cardiology_observation_and_range() -> None:
    p = project(copy.deepcopy(CARDIOLOGY), {})
    assert p and p.observations[0].loinc_code == "10230-1"
    assert (p.observations[0].ref_low, p.observations[0].ref_high) == (50.0, 70.0)


def test_dental_and_unknown_unit() -> None:
    raw = {"teeth": [{"fdi": leaf("16"), "condition": "caries", "severity": "mild"}]}
    p = project(raw, {})
    assert p and p.conditions[0].label == "caries (FDI 16)" and p.conditions[0].finding is None
    assert project({"other": 1}, {}) is None
