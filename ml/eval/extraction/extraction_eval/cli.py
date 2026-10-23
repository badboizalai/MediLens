"""CLI: python -m extraction_eval {run,gen-baseline} (run from ml/eval/extraction)."""

import argparse
import json
import sys
from pathlib import Path

from . import baseline, metrics

HERE = Path(__file__).resolve().parent.parent
DEFAULT_GOLD = HERE.parent / "golden-v1" / "gold.jsonl"
DEFAULT_PRED = HERE / "baseline" / "predictions.jsonl"
DEFAULT_THRESHOLDS = HERE / "thresholds.json"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def to_markdown(report, fails, thresholds, banner):
    o, ra, cv = report["overall"], report["region_accuracy"], report["citation_validity"]
    lines = ["# Extraction evaluation", ""]
    if banner:
        lines += [f"> **{banner}**", ""]
    lines += [
        f"Gate: **{'FAIL' if fails else 'PASS'}** | gold docs {report['gold_docs']} | "
        f"pred docs {report['pred_docs']}",
        "",
        "| Metric | Value | Threshold |",
        "| --- | --- | --- |",
        f"| Field F1 (overall) | {o['f1']:.3f} | >= {thresholds['field_f1_overall']} |",
        f"| Region accuracy | {ra['value']:.3f} ({ra['correct']}/{ra['total']}) | "
        f">= {thresholds['region_accuracy']} |",
        f"| Citation validity | {cv['value']:.3f} ({cv['valid']}/{cv['total']}) | "
        f">= {thresholds['citation_validity']} |",
        "",
        "| Group | Precision | Recall | F1 (exact) | F1 (fuzzy) |",
        "| --- | --- | --- | --- | --- |",
        f"| ALL | {o['precision']:.3f} | {o['recall']:.3f} | {o['f1']:.3f} | {o['f1_fuzzy']:.3f} |",
    ]
    for grp, s in report["groups"].items():
        lines.append(
            f"| {grp} | {s['precision']:.3f} | {s['recall']:.3f} | {s['f1']:.3f} | "
            f"{s['f1_fuzzy']:.3f} |"
        )
    lines += ["", "## Weakest field paths (F1, by unit)", "", "| unit | path | F1 | tp | fp | fn |"]
    lines.append("| --- | --- | --- | --- | --- | --- |")
    rows = [(u, p, s) for u, ps in report["per_field_path"].items() for p, s in ps.items()]
    for u, p, s in sorted(rows, key=lambda r: (r[2]["f1"], r[0], r[1]))[:10]:
        lines.append(f"| {u} | `{p}` | {s['f1']:.3f} | {s['tp']} | {s['fp']} | {s['fn']} |")
    if fails:
        lines += ["", "## Gate failures", ""] + [f"- {f}" for f in fails]
    return "\n".join(lines) + "\n"


def cmd_run(a):
    gold = {r["doc_id"]: r for r in load(a.gold)}
    preds = load(a.pred)
    pred = {r["doc_id"]: r for r in preds}
    if not gold.keys() & pred.keys():
        return no_predictions(a, len(gold))
    thresholds = json.loads(Path(a.thresholds).read_text(encoding="utf-8"))
    report = metrics.score(gold, pred, fuzzy=a.fuzzy)
    fails = metrics.check_gate(report, thresholds)
    banner = baseline.LABEL if any(r.get("_label") == baseline.LABEL for r in preds) else ""
    report.update(gate={"passed": not fails, "failures": fails}, thresholds=thresholds)
    md = to_markdown(report, fails, thresholds, banner)
    print(md)
    if a.out_dir:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out / "report.md").write_text(md, encoding="utf-8")
    return 1 if fails else 0


def no_predictions(a, n_gold):
    """Nothing to score for this gold set: say so, never invent an F1."""
    msg = (
        f"no predictions for {n_gold} gold docs in {a.gold}: F1 not computed (no model results yet)"
    )
    print(msg)
    if a.out_dir:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        report = {"status": "no_predictions", "gold_docs": n_gold}
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (out / "report.md").write_text(f"# Extraction evaluation\n\n{msg}\n", encoding="utf-8")
    return 0


def cmd_gen_baseline(a):
    text = baseline.dumps(baseline.generate(load(a.gold)))
    if a.check:
        return 0 if Path(a.out).read_text(encoding="utf-8") == text else 1
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="utf-8")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="extraction_eval")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="score predictions and apply the gate")
    r.add_argument("--gold", default=str(DEFAULT_GOLD))
    r.add_argument("--pred", default=str(DEFAULT_PRED))
    r.add_argument("--thresholds", default=str(DEFAULT_THRESHOLDS))
    r.add_argument("--out-dir")
    r.add_argument("--fuzzy", type=float, default=0.9)
    r.set_defaults(fn=cmd_run)
    g = sub.add_parser("gen-baseline", help="regenerate the oracle-with-noise baseline")
    g.add_argument("--gold", default=str(DEFAULT_GOLD))
    g.add_argument("--out", default=str(DEFAULT_PRED))
    g.add_argument("--check", action="store_true", help="exit 1 if the committed file differs")
    g.set_defaults(fn=cmd_gen_baseline)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
