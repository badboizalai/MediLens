import json
from pathlib import Path

from extraction_eval import baseline, cli, metrics

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT.parent / "golden-v1" / "gold.jsonl"


def cite(quote, page=1):
    return {"page": page, "quote": quote}


def tooth(fdi, cond, code, quote="Răng 14"):
    return {
        "fdi": {"value": fdi, "confidence": 1.0, "source": cite(quote)},
        "condition": cond,
        "region": {"confidence": 1.0, "region_code": code},
    }


def rec(doc_id, teeth, unit="dental"):
    return {"doc_id": doc_id, "unit": unit, "quality": "good", "fields": {"teeth": teeth}}


def run(gold_recs, pred_recs, **kw):
    return metrics.score(
        {r["doc_id"]: r for r in gold_recs}, {r["doc_id"]: r for r in pred_recs}, **kw
    )


def test_perfect_prediction_scores_one():
    g = [rec("d1", [tooth("14", "caries", "tooth_14")])]
    r = run(g, g)
    assert r["overall"]["f1"] == 1.0
    assert r["region_accuracy"]["value"] == 1.0
    assert r["citation_validity"]["value"] == 1.0


def test_prf_counts_missing_wrong_and_extra():
    g = [rec("d1", [tooth("14", "caries", "tooth_14")])]
    # condition wrong (fp+fn), plus an extra tooth (3 extra fields -> fp)
    p = [rec("d1", [tooth("14", "filling", "tooth_14"), tooth("15", "x", "tooth_15")])]
    o = run(g, p)["overall"]
    assert (o["tp"], o["fn"]) == (2, 1)  # fdi + region_code match, condition missed
    assert o["fp"] == 1 + 3  # wrong condition + extra tooth fields
    assert o["recall"] == 2 / 3


def test_missing_prediction_doc_is_all_fn():
    g = [rec("d1", [tooth("14", "caries", "tooth_14")])]
    r = run(g, [])
    assert r["overall"]["recall"] == 0.0
    assert r["missing_pred_docs"] == 1


def test_per_unit_and_per_field_path():
    g = [
        rec("d1", [tooth("14", "caries", "tooth_14")]),
        {"doc_id": "d2", "unit": "cardiology", "fields": {"lvef": "55"}},
    ]
    p = [g[0], {"doc_id": "d2", "unit": "cardiology", "fields": {"lvef": "40"}}]
    r = run(g, p)
    assert r["groups"]["unit=dental"]["f1"] == 1.0
    assert r["groups"]["unit=cardiology"]["f1"] == 0.0
    assert "teeth[].condition" in r["per_field_path"]["dental"]
    assert r["per_field_path"]["cardiology"]["lvef"]["fn"] == 1


def test_list_order_does_not_matter():
    a, b = tooth("14", "caries", "tooth_14"), tooth("21", "filling", "tooth_21")
    assert run([rec("d", [a, b])], [rec("d", [b, a])])["overall"]["f1"] == 1.0


def test_region_accuracy_ignores_null_gold_codes():
    g = [rec("d", [tooth("14", "c", "tooth_14"), tooth("21", "c", None)])]
    p = [rec("d", [tooth("14", "c", "tooth_15"), tooth("21", "c", "tooth_21")])]
    ra = run(g, p)["region_accuracy"]
    assert (ra["correct"], ra["total"]) == (0, 1)


def test_citation_validity_rules():
    g = [rec("d", [tooth("14", "c", "tooth_14", quote="Răng 14")])]
    for bad in (
        cite("invented text"),
        cite("Răng 14", page=0),
        cite("", page=1),
        cite("Răng 14", 2),
    ):
        p = [rec("d", [tooth("14", "c", "tooth_14")])]
        p[0]["fields"]["teeth"][0]["fdi"]["source"] = bad
        assert run(g, p)["citation_validity"]["value"] == 0.0
    ok = [rec("d", [tooth("14", "c", "tooth_14", quote="  răng 14 ")])]
    assert run(g, ok)["citation_validity"]["value"] == 1.0


def test_fuzzy_f1_forgives_vietnamese_tone_placement():
    g = [{"doc_id": "d", "unit": "u", "fields": {"site": "thùy phải"}}]
    p = [{"doc_id": "d", "unit": "u", "fields": {"site": "thuỳ phải"}}]
    o = run(g, p)["overall"]
    assert o["f1"] == 0.0 and o["f1_fuzzy"] == 1.0


def test_gate_flags_each_regression():
    g = [rec("d1", [tooth("14", "caries", "tooth_14")])]
    bad = [rec("d1", [tooth("14", "filling", "tooth_99", quote="made up")])]
    t = json.loads((ROOT / "thresholds.json").read_text())
    t["min_gold_docs"] = 1
    fails = metrics.check_gate(run(g, bad), t)
    text = " ".join(fails)
    for name in ("field F1 (overall)", "unit=dental", "region accuracy", "citation validity"):
        assert name in text
    assert metrics.check_gate(run(g, g), t) == []


def test_baseline_is_deterministic_and_committed_file_is_current():
    gold = cli.load(GOLD)
    assert baseline.dumps(baseline.generate(gold)) == baseline.dumps(baseline.generate(gold))
    committed = (ROOT / "baseline" / "predictions.jsonl").read_text(encoding="utf-8")
    assert committed == baseline.dumps(baseline.generate(gold))


def test_baseline_passes_gate_and_is_labelled():
    gold = cli.load(GOLD)
    preds = cli.load(ROOT / "baseline" / "predictions.jsonl")
    assert all(r["_label"].startswith("NOT_A_MODEL_RESULT") for r in preds)
    r = metrics.score({x["doc_id"]: x for x in gold}, {x["doc_id"]: x for x in preds})
    t = json.loads((ROOT / "thresholds.json").read_text())
    assert metrics.check_gate(r, t) == []
    assert r["overall"]["f1"] < 1.0  # noise really is injected


def test_strata_groups_and_no_predictions(tmp_path, capsys):
    g = rec("d1", [tooth("14", "caries", "tooth_14")])
    g["strata"] = {"lang": "vi", "noise": "heavy"}
    r = run([g], [g])
    assert r["groups"]["lang=vi"]["f1"] == 1.0
    assert "noise=heavy@unit=dental" in r["groups"]
    gold = tmp_path / "gold.jsonl"
    gold.write_text(json.dumps(g) + "\n", encoding="utf-8")
    pred = tmp_path / "pred.jsonl"
    pred.write_text(json.dumps(rec("other", [])) + "\n", encoding="utf-8")
    assert cli.main(["run", "--gold", str(gold), "--pred", str(pred)]) == 0
    assert "no predictions" in capsys.readouterr().out


def conf_tooth(fdi, cond, code, c, quote="Răng 14"):
    t = tooth(fdi, cond, code, quote)
    t["fdi"]["confidence"] = t["region"]["confidence"] = c
    return t


def test_calibration_ece_hand_computed():
    # 4 pairs at 0.9 (3 right): gap 0.15 each; 2 pairs at 0.3 (0 right): gap 0.3 each
    pairs = [(0.9, True)] * 3 + [(0.9, False)] + [(0.3, False)] * 2
    c = metrics.calibration(pairs)
    assert abs(c["ece"] - (4 * 0.15 + 2 * 0.3) / 6) < 1e-9
    assert c["n_conf_ge_0.7"] == 4 and c["error_rate_conf_ge_0.7"] == 0.25
    assert metrics.calibration([(1.0, True)])["bins"][9]["n"] == 1  # conf 1.0 -> last bin
    assert metrics.calibration([])["ece"] is None


def test_score_ece_overconfident_wrong_fields():
    g = [rec("d1", [tooth("14", "caries", "tooth_14")])]
    p = [rec("d1", [conf_tooth("14", "filling", "tooth_14", 1.0)])]
    p[0]["fields"]["teeth"][0]["condition"] = {"value": "filling", "confidence": 1.0}
    cal = run(g, p)["calibration"]
    # fdi + region_code right, condition wrong, all at conf 1.0 -> acc 2/3 -> ECE 1/3
    assert cal["ALL"]["n"] == 3 and abs(cal["ALL"]["ece"] - 1 / 3) < 1e-9
    assert "unit=dental" in cal


def test_region_accuracy_by_unit_and_ece_gate():
    g = [rec("d1", [tooth("14", "c", "tooth_14")])]
    p = [rec("d1", [conf_tooth("14", "c", "tooth_15", 1.0)])]
    r = run(g, p)
    assert r["region_accuracy_by_unit"]["dental"] == {"value": 0.0, "correct": 0, "total": 1}
    t = json.loads((ROOT / "thresholds.json").read_text())
    assert any("ECE" in f for f in metrics.check_gate(r, t))
    assert not any("ECE" in f for f in metrics.check_gate(run(g, []), t))  # no confidences: skip
