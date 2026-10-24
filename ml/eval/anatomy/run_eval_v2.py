"""Region accuracy of the rules-only `map_region` on golden-v2 gold location strings (S11-T108).

Input = the gold source quote of each location field (tooth FDI, site, node station), i.e. perfect
OCR and perfect extraction: this isolates the mapper, it is NOT end-to-end region accuracy.
Writes a machine-readable result next to this file.

Usage: python3 ml/eval/anatomy/run_eval_v2.py [--out ml/eval/anatomy/results_v2.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "worker" / "src"))

from medilens_worker.anatomy import map_region  # noqa: E402

GOLD = ROOT / "ml" / "eval" / "golden-v2" / "gold.jsonl"
TARGET = 0.85
# (list or object key, key holding the location text)
LOCATION_FIELDS = (
    ("teeth", "fdi"),
    ("diagnoses", "site"),
    ("primary", "site"),
    ("metastases", "site"),
    ("nodes", "station"),
)


def items(path=GOLD):
    """(doc_id, unit, strata, kind, text, gold_code) for every item with a gold region_code."""
    for line in Path(path).read_text("utf-8").splitlines():
        d = json.loads(line)
        for kind, loc in LOCATION_FIELDS:
            v = d["fields"].get(kind) or []
            for x in [v] if isinstance(v, dict) else v:
                code = (x.get("region") or {}).get("region_code")
                if code and x.get(loc):
                    yield (
                        d["doc_id"],
                        d["unit"],
                        d.get("strata", {}),
                        kind,
                        x[loc]["source"]["quote"],
                        code,
                    )


def evaluate(path=GOLD):
    groups = defaultdict(lambda: [0, 0])  # name -> [correct, total]
    errors = []
    for doc_id, unit, strata, kind, text, gold in items(path):
        got = map_region(text, unit)[0]
        names = ["ALL", f"unit={unit}", f"kind={unit}/{kind}"]
        names += [f"{k}={v}" for k, v in sorted(strata.items())]
        for n in names:
            groups[n][0] += got == gold
            groups[n][1] += 1
        if got != gold:
            errors.append({"doc": doc_id, "text": text, "gold": gold, "got": got})
    return {
        "gold": str(Path(path).relative_to(ROOT)),
        "target": TARGET,
        "groups": {
            n: {"accuracy": c / t, "correct": c, "total": t} for n, (c, t) in sorted(groups.items())
        },
        "errors": errors,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out", type=Path, default=ROOT / "ml" / "eval" / "anatomy" / "results_v2.json"
    )
    args = ap.parse_args()
    res = evaluate()
    args.out.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", "utf-8")
    for n, g in res["groups"].items():
        print(f"{n:40s} {g['accuracy']:.3f}  ({g['correct']}/{g['total']})")
    print(f"errors: {len(res['errors'])}")
