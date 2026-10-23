"""Evaluate the rules page classifier on golden-v1 ground-truth page text.

golden-v1 has no page-type labels, so labels are derived from `unit`:
dental -> dental_record; cardiology/oncology -> outpatient_form (every page is a visit form).
Text = what synth_gen renders (header + body + footer), regenerated from the seeded generator.

Usage: python ml/eval/classify/run_eval.py [--out ml/eval/classify/REPORT.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ml" / "datasets" / "synth"))
sys.path.insert(0, str(ROOT / "apps" / "worker" / "src"))

from medilens_worker.classify.page_types import PageType  # noqa: E402
from medilens_worker.classify.rules import LLM_FALLBACK_THRESHOLD, classify_text  # noqa: E402
from synth_gen import generate  # noqa: E402

FOOTER = "SYNTHETIC - TEST ONLY"
LABEL = {"dental": PageType.DENTAL_RECORD, "cardiology": PageType.OUTPATIENT_FORM,
         "oncology": PageType.OUTPATIENT_FORM}  # fmt: skip
GOLDEN = ROOT / "ml" / "eval" / "golden-v1"


def evaluate() -> tuple[list[tuple[str, PageType, PageType, float]], int]:
    seed = json.loads(next((GOLDEN / "records").glob("*.json")).read_text("utf-8"))["metadata"][
        "seed"
    ]
    rows = []
    for i, spec in enumerate(generate.plan(seed, "v1")):
        rec, header, lines = generate.generate_record(i, spec, seed, "v1")
        pred, conf = classify_text("\n".join([*header, *lines, FOOTER]))
        rows.append((rec["doc_id"], LABEL[spec["unit"]], pred, conf))
    return rows, seed


def report(rows: list[tuple[str, PageType, PageType, float]], seed: int) -> str:
    n = len(rows)
    ok = sum(t == p for _, t, p, _ in rows)
    low = sum(c < LLM_FALLBACK_THRESHOLD for *_, c in rows)
    conf = Counter((t.value, p.value) for _, t, p, _ in rows)
    wrong = [f"{d} ({t.value} -> {p.value}, {c})" for d, t, p, c in rows if t != p]
    out = [
        "# Page classifier (rules) - golden-v1 evaluation",
        "",
        f"- Pages: {n} (golden-v1, seed {seed}, clean text, one page per record)",
        f"- Accuracy: **{ok / n:.3f}** ({ok}/{n}); target >= 0.90",
        f"- Below LLM fallback threshold ({LLM_FALLBACK_THRESHOLD}): {low}",
        "",
        "## Confusion (true -> predicted : count)",
        "",
        *[f"- {t} -> {p}: {c}" for (t, p), c in sorted(conf.items())],
        "",
        "## Misclassified ids",
        "",
        *([f"- {w}" for w in wrong] or ["- none"]),
        "",
        "## Caveats",
        "",
        "- golden-v1 carries no page-type labels; labels are derived from `unit` (see script).",
        "- Only 2 of the 9 types occur (dental_record, outpatient_form); the other 7 are covered",
        "  only by unit-test snippets in `apps/worker/tests/classify`. Accuracy here is optimistic:",
        "  one template per unit, clean text, no OCR noise. Re-run on real-OCR text and on a",
        "  9-type labelled set (plan 25.1: 30 per type) before relying on it.",
    ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    text = report(*evaluate())
    if a.out:
        a.out.write_text(text, encoding="utf-8")
    print(text)
