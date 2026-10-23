"""Region accuracy of map_region on golden-v1 labelled locations.

Scored: items whose gold `region.region_code` is non-null (dental teeth, liver). All other items
are null by design (see golden-v1 DATASET_CARD) and are only counted as coverage, not scored.

Usage: python ml/eval/anatomy/run_eval.py [--out ml/eval/anatomy/REPORT.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "worker" / "src"))

from medilens_worker.anatomy import map_region  # noqa: E402

GOLD = ROOT / "ml" / "eval" / "golden-v1" / "gold.jsonl"
TARGET = 0.85


def items():
    """(doc_id, kind, text, unit, gold_code) for every item carrying a region object."""
    for line in GOLD.read_text("utf-8").splitlines():
        d = json.loads(line)
        unit = d["doc_id"].split("-")[2]
        f = d["fields"]
        for t in f.get("teeth", []):
            yield (
                d["doc_id"],
                "teeth",
                t["fdi"]["source"]["quote"],
                unit,
                t["region"]["region_code"],
            )
        for kind in ("diagnoses", "primary", "metastases"):
            v = f.get(kind) or []
            for x in [v] if isinstance(v, dict) else v:
                if x.get("site") and x.get("region"):
                    yield d["doc_id"], kind, x["site"]["value"], unit, x["region"]["region_code"]


def evaluate():
    rows = [(*it, *map_region(it[2], it[3])) for it in items()]
    scored = [r for r in rows if r[4] is not None]
    ok = sum(r[5] == r[4] for r in scored)
    return rows, scored, ok


def report(rows, scored, ok) -> str:
    acc = ok / len(scored)
    by_kind = Counter(r[1] for r in scored)
    wrong = [r for r in scored if r[5] != r[4]]
    unl = [r for r in rows if r[4] is None]
    mapped = sum(r[5] is not None for r in unl)
    out = [
        "# Anatomy mapping eval (S7-T66)",
        "",
        "Rules-only `map_region` on golden-v1 (`ml/eval/golden-v1/gold.jsonl`). "
        "Input = the source quote of the location field; unit from the doc id.",
        "",
        f"- Labelled items scored: **{len(scored)}** "
        + "("
        + ", ".join(f"{k} {n}" for k, n in sorted(by_kind.items()))
        + ")",
        f"- **Region accuracy: {acc:.3f}** ({ok}/{len(scored)}), target >= {TARGET} -> "
        + ("PASS" if acc >= TARGET else "FAIL"),
        f"- Errors: {len(wrong)}",
        "",
        "## Caveats (honest reading)",
        "",
        "- golden-v1 labels regions only for dental teeth (`tooth_<FDI>`) and liver metastases; "
        f"the other {len(unl)} location items have `region_code = null` by design, so region "
        "accuracy for cardiology and most oncology sites is **not measurable** yet.",
        "- The scored set is mostly clean synthetic text (`Răng 14`, `Gan`); expect lower accuracy on "
        "real OCR output. Laterality, ranges and invalid numbers are covered by unit tests instead.",
        f"- Coverage on unlabelled items (not scored): mapper returned a code for {mapped}/{len(unl)}.",
    ]
    if wrong:
        out += ["", "## Errors", "", "| doc | text | gold | got |", "|---|---|---|---|"]
        out += [f"| {r[0]} | {r[2]} | {r[4]} | {r[5]} |" for r in wrong[:30]]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "ml" / "eval" / "anatomy" / "REPORT.md")
    args = ap.parse_args()
    text = report(*evaluate())
    args.out.write_text(text, "utf-8")
    print(text)
