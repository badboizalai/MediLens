"""Re-emit reference page text for golden-v0 from the seeded synth generator.

Usage: uv run python -m bakeoff.make_reference --golden ../golden-v0
The text equals what render_clean() draws (header + body lines + footer stamp), so it is the
exact ground truth for every image variant. Checks doc_ids against gold.jsonl.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bakeoff.golden import DEFAULT_REFERENCE

FOOTER = "SYNTHETIC - TEST ONLY"  # drawn by synth_gen.render.render_clean on every page
SYNTH_DIR = Path(__file__).resolve().parents[3] / "datasets" / "synth"


def build(golden: Path, synth_dir: Path = SYNTH_DIR) -> list[dict]:
    sys.path.insert(0, str(synth_dir))
    from synth_gen import generate  # noqa: PLC0415 - path injected above

    seed = json.loads(next((golden / "records").glob("*.json")).read_text("utf-8"))["metadata"][
        "seed"
    ]
    gold_ids = [
        json.loads(line)["doc_id"]
        for line in (golden / "gold.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    out = []
    for i, spec in enumerate(generate.plan(seed)):
        rec, header, lines = generate.generate_record(i, spec, seed)
        out.append({"doc_id": rec["doc_id"], "text": "\n".join([*header, *lines, FOOTER])})
    if [r["doc_id"] for r in out] != gold_ids:
        raise SystemExit("regenerated doc_ids differ from gold.jsonl: generator/seed drift")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=DEFAULT_REFERENCE)
    a = ap.parse_args()
    rows = build(a.golden)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    print(f"wrote {len(rows)} reference texts to {a.out}")


if __name__ == "__main__":
    main()
