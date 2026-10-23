"""Evaluate the rules page classifier on the 9-type synthetic text set (S6-T54c).

Pages come from `synth_gen.pages` (seeded, text-level, VI/EN mix). Rules are tuned on the `dev`
split only; the headline numbers are on the held-out `test` split. UNKNOWN (no rule fired) counts
as a miss for every label, including `other`.

Usage: python ml/eval/classify/run_eval.py [--out ml/eval/classify/REPORT.md] [--split test|dev]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ml" / "datasets" / "synth"))
sys.path.insert(0, str(ROOT / "apps" / "worker" / "src"))

from medilens_worker.classify.rules import LLM_FALLBACK_THRESHOLD, classify_text  # noqa: E402
from synth_gen.pages import TYPES, generate_pages  # noqa: E402

SEED = 20261023
MACRO_TARGET = 0.90


NOTES = """
## Before / after rule changes (macro-F1)

Changes made on `dev` only: title-line bonus (strong match in first 2 lines +2), `other` rules,
`phieu sieu am`. Before: dev 0.827, test 0.861 (lab/imaging/dental false positives from distractor
lines; `other` never predicted). After: dev 1.000, test 1.000.

## Caveats

- 1.000 is optimistic: synthetic templates, clean text, no OCR noise, 4-5 title variants per type,
  written knowing the rule vocabulary. It shows the target is *measurable* and the rules work on
  clean text; it is not evidence for real scans. The old golden-v1 run (2 types) is superseded.
- Real-OCR evidence (D55) is still missing, see below.

## Offline OCR baseline (image -> OCR -> classify): not run

No `tesseract` binary, PaddleOCR or VietOCR is installed here, and none was installed (heavy).
To run it: (1) render page images (`synth_gen`, needs `pillow` and DejaVu Sans); (2) OCR with
PaddleOCR (`paddlepaddle` CPU + `paddleocr`, ~0.5-1 GB of wheels, det+rec weights ~15-30 MB
downloaded on first run) or `apt install tesseract-ocr tesseract-ocr-vie` (~30 MB) +
`pytesseract`; ~1-3 s/page on CPU, ~10 min for 255 pages; (3) feed the text to `classify_text`
and compare macro-F1 with this report. golden-v1 images carry no page-type labels, so the OCR run
needs images rendered from `synth_gen.pages` (that render step is not written yet).
"""


def evaluate(split: str) -> list[tuple[str, str, str, float]]:
    """(id, true, predicted, confidence) for every page of the split."""
    rows = []
    for p in generate_pages(SEED):
        if p["split"] == split:
            pred, conf = classify_text(p["text"])
            rows.append((p["id"], p["label"], pred.value, conf))
    return rows


def prf(rows: list[tuple[str, str, str, float]]) -> dict[str, tuple[float, float, float, int]]:
    out = {}
    for t in TYPES:
        tp = sum(a == t and b == t for _, a, b, _ in rows)
        fp = sum(a != t and b == t for _, a, b, _ in rows)
        fn = sum(a == t and b != t for _, a, b, _ in rows)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        out[t] = (p, r, 2 * p * r / (p + r) if p + r else 0.0, tp + fn)
    return out


def report(rows: list[tuple[str, str, str, float]], split: str) -> str:
    m = prf(rows)
    macro = sum(v[2] for v in m.values()) / len(m)
    acc = sum(a == b for _, a, b, _ in rows) / len(rows)
    low = sum(c < LLM_FALLBACK_THRESHOLD for *_, c in rows)
    cols = [*TYPES, "unknown"]
    conf = Counter((a, b) for _, a, b, _ in rows)
    wrong = [f"{i} ({a} -> {b}, {c})" for i, a, b, c in rows if a != b]
    out = [
        f"# Page classifier (rules) - 9-type synthetic set, `{split}` split",
        "",
        f"- Pages: {len(rows)} ({len(rows) // len(TYPES)} per type, seed {SEED}, text-level, VI/EN)",
        f"- Macro-F1: **{macro:.3f}** (target >= {MACRO_TARGET}); accuracy {acc:.3f}",
        f"- Below LLM fallback threshold ({LLM_FALLBACK_THRESHOLD}): {low}",
        "",
        "## Per-type",
        "",
        "| type | support | precision | recall | F1 |",
        "|---|---|---|---|---|",
        *[f"| {t} | {n} | {p:.3f} | {r:.3f} | {f:.3f} |" for t, (p, r, f, n) in m.items()],
        "",
        "## Confusion matrix (rows = true, columns = predicted)",
        "",
        "| true \\ pred | " + " | ".join(cols) + " |",
        "|---|" + "---|" * len(cols),
        *[f"| {t} | " + " | ".join(str(conf[(t, c)]) for c in cols) + " |" for t in TYPES],
        "",
        "## Misclassified ids",
        "",
        *([f"- {w}" for w in wrong] or ["- none"]),
    ]
    return "\n".join(out) + "\n" + NOTES


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    a = ap.parse_args()
    text = report(evaluate(a.split), a.split)
    if a.out:
        a.out.write_text(text, encoding="utf-8")
    print(text)
