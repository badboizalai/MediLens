import pytest
import yaml
from medilens_worker.anatomy import InvalidFdi, map_region, parse_fdi
from medilens_worker.anatomy.fdi import TERMINOLOGY_DIR
from medilens_worker.anatomy.mapper import tree


@pytest.mark.parametrize(
    "text,expected",
    [
        ("răng 36", ["36"]),
        ("Tooth 36", ["36"]),
        ("R36", ["36"]),
        ("răng 36, 37", ["36", "37"]),
        ("răng 11-13", ["11", "12", "13"]),
        ("teeth 36 and 37", ["36", "37"]),
        ("răng 51-55", ["51", "52", "53", "54", "55"]),
        ("răng 85", ["85"]),
        ("viêm gan B", []),
        ("36, 37", []),  # bare numbers need a dental context
    ],
)
def test_parse_fdi(text, expected):
    assert parse_fdi(text) == expected


def test_bare_list_in_dental_context():
    assert parse_fdi("36, 37", dental_context=True) == ["36", "37"]


@pytest.mark.parametrize("text", ["răng 19", "tooth 49", "răng 86", "răng 11-23", "răng 56"])
def test_parse_fdi_rejects_invalid(text):
    with pytest.raises(InvalidFdi):
        parse_fdi(text)


@pytest.mark.parametrize(
    "text,unit,code",
    [
        ("Răng 36", "dental", "tooth_36"),
        ("tooth 85", None, "tooth_85"),
        ("răng 11-13", "dental", "quadrant_1"),
        ("răng 36, 46", "dental", "jaw_lower"),
        ("răng 16, 36", "dental", None),
        ("răng 19", "dental", None),
        ("Van hai lá", "cardiology", "valve_mitral"),
        ("Mitral valve", None, "valve_mitral"),
        ("Gan", "oncology", "liver"),
        ("Liver", "oncology", "liver"),
        ("Động mạch vành", None, "coronary_arteries"),
        ("Động mạch vành phải", None, "cor_rca"),
        ("Động mạch vành trái", None, "coronary_arteries"),  # LAD/LCX/LMCA: not guessed
        ("Phổi phải", None, "lung_r"),
        ("Phoi trai", None, "lung_l"),
        ("left lung", None, "lung_l"),
        ("Right breast", None, "breast_r"),
        ("Tâm nhĩ trái", None, "heart_la"),
        ("Tâm nhĩ", None, "heart"),
        ("phổi hai bên", None, None),
        ("bilateral kidneys", None, None),
        ("phổi trái và phải", None, None),
        ("Phổi", None, None),
        ("both lungs", None, None),
        ("thận", None, None),
        ("Phổi (thùy trên) trái", None, "lung_l"),
        ("Tim", None, "heart"),
        ("Phổi (thùy trên)", None, None),
        ("hạch rốn phổi trái", None, "ln_hilar_l"),  # longest phrase masks "phổi"
        ("phổi trái, gan", None, None),  # two regions: do not pick one
        ("xin chào", None, None),
        ("", None, None),
    ],
)
def test_map_region(text, unit, code):
    got, conf = map_region(text, unit)
    assert got == code
    assert (conf > 0) == (code is not None)


def test_all_codes_exist_in_tree():
    rows = yaml.safe_load((TERMINOLOGY_DIR / "location-synonyms.v1.yaml").read_text("utf-8"))
    for r in rows:
        for k in ("code", "right", "left"):
            assert r.get(k, "body") in tree(), r
