import unicodedata

import pytest

from bakeoff.metrics import aggregate, cer_counts, levenshtein, normalize


def test_levenshtein_basic():
    assert levenshtein("", "abc") == 3
    assert levenshtein("kitten", "sitting") == 3
    assert levenshtein("abc", "abc") == 0


def test_normalize_nfc_and_whitespace():
    nfd = unicodedata.normalize("NFD", "Nguyễn  Văn\n Test")
    assert nfd != "Nguyễn Văn Test"
    assert normalize(nfd) == "Nguyễn Văn Test"


def test_cer_nfd_prediction_equals_nfc_reference():
    ref = "Răng 24 sâu răng"
    pred = unicodedata.normalize("NFD", ref)
    edits, chars = cer_counts(ref, pred)
    assert (edits, chars) == (0, len(ref))


def test_cer_diacritic_error_costs_one_char():
    edits, chars = cer_counts("Bệnh viện", "Benh viện")
    assert edits == 1  # precomposed ệ -> e is a single substitution after NFC
    assert chars == len("Bệnh viện")


def test_cer_line_breaks_ignored():
    assert cer_counts("a b\nc", "a b c")[0] == 0


def test_cer_empty_prediction_is_100_percent():
    assert cer_counts("abc", "") == (3, 3)


def test_aggregate_micro_average_and_groups():
    rows = [
        {"lang": "vi", "quality": "good", "variant": "clean", "edits": 1, "chars": 10},
        {"lang": "vi", "quality": "poor", "variant": "perspective", "edits": 4, "chars": 10},
        {"lang": "en", "quality": "good", "variant": "clean", "edits": 0, "chars": 20},
    ]
    agg = aggregate(rows)
    assert agg["overall"] == pytest.approx(5 / 40)
    assert agg["by_lang"]["vi"] == pytest.approx(5 / 20)
    assert agg["by_lang"]["en"] == 0.0
    assert agg["by_quality"]["good"] == pytest.approx(1 / 30)
    assert agg["by_quality"]["poor"] == pytest.approx(0.4)
    assert agg["by_variant"]["clean"] == pytest.approx(1 / 30)
    assert agg["by_variant"]["perspective"] == pytest.approx(0.4)


def test_aggregate_empty():
    assert aggregate([])["overall"] is None
