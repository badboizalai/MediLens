"""Deterministic generator for golden-v0.

uv run --with pillow python -m synth_gen.generate --out ml/eval/golden-v0 [--seed 20260101] [--no-images]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from . import content, render

GENERATOR_VERSION = "0.2.0"
DEFAULT_SEED = 20260101
UNIT_COUNTS = [("dental", 17), ("cardiology", 17), ("oncology", 16)]
QUALITY_COUNTS = [("good", 25), ("medium", 18), ("poor", 7)]  # 50/35/15 %


def plan(seed: int) -> list[dict]:
    """Per-record (unit, lang, quality) assignment; every 5th record is English."""
    rng = random.Random(seed)  # noqa: S311 - deterministic synthetic data
    units = [u for u, n in UNIT_COUNTS for _ in range(n)]
    qualities = [q for q, n in QUALITY_COUNTS for _ in range(n)]
    rng.shuffle(qualities)
    return [
        {"unit": u, "lang": "en" if i % 5 == 4 else "vi", "quality": q}
        for i, (u, q) in enumerate(zip(units, qualities, strict=True))
    ]


def variant_subset(seed: int, n: int = 10) -> dict[int, str]:
    """Seeded ~20 % of records get an extra variant: half handwriting, half perspective.

    Uses its own RNG so existing plan/records are unchanged.
    """
    rng = random.Random(f"{seed}:variants")  # noqa: S311 - deterministic synthetic data
    picked = rng.sample(range(sum(c for _, c in UNIT_COUNTS)), n)
    return {i: ("handwriting" if k % 2 == 0 else "perspective") for k, i in enumerate(picked)}


def generate_record(index: int, spec: dict, seed: int) -> tuple[dict, list[str], list[str]]:
    """Returns (record dict without images, header lines, body lines)."""
    rng = random.Random(f"{seed}:{index}")  # noqa: S311 - deterministic synthetic data
    lang, unit = spec["lang"], spec["unit"]
    lab = content.LABELS[lang]
    patient = content.make_patient(rng)
    header = [
        lab["title"],
        f"{lab['patient']}: {patient['name']}",
        f"{lab['birth']}: {patient['birth_year']}    {lab['sex']}: "
        f"{lab['female'] if patient['sex'] == 'female' else lab['male']}",
    ]
    lines: list[str] = []
    fields = content.BUILDERS[unit](rng, lang, lines)
    doc_id = f"gv0-{index + 1:03d}-{unit}-{lang}"
    record = {
        "doc_id": doc_id,
        "unit": unit,
        "quality": spec["quality"],
        "fields": fields,
        "metadata": {
            "synthetic": True,
            "lang": lang,
            "patient": patient,
            "seed": seed,
            "generator_version": GENERATOR_VERSION,
            "images": [],
        },
    }
    return record, header, lines


def generate(out: Path, seed: int = DEFAULT_SEED, images: bool = True) -> list[dict]:
    (out / "records").mkdir(parents=True, exist_ok=True)
    if images:
        (out / "images").mkdir(exist_ok=True)
    records = []
    extra = variant_subset(seed)
    for i, spec in enumerate(plan(seed)):
        rec, header, lines = generate_record(i, spec, seed)
        if images:
            rng = random.Random(f"{seed}:{i}:img")  # noqa: S311 - deterministic synthetic data
            clean = render.render_clean(header, lines)
            variants = [("clean", clean, [])]
            if spec["quality"] != "good":
                deg, ops = render.degrade(clean, spec["quality"], rng)
                variants.append(("degraded", deg, ops))
            kind = extra.get(i)
            if kind == "handwriting":
                hand = render.render_clean(header, lines, random.Random(f"{seed}:{i}:hand"))  # noqa: S311
                variants.append(
                    ("handwriting", hand, [{"type": "handwriting", "font": "DejaVuSans-jitter"}])
                )
            elif kind == "perspective":
                warped, wops = render.perspective(clean, rng)
                variants.append(("perspective", warped, wops))
            for name, img, ops in variants:
                rel = f"images/{rec['doc_id']}_{name}.jpg"
                render.to_jpeg(img, out / rel, 80)
                rec["metadata"]["images"].append(
                    {"file": rel, "variant": name, "degradations": ops, "jpeg_quality": 80}
                )
        (out / "records" / f"{rec['doc_id']}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        records.append(rec)
    # JSONL in the format expected by .claude/skills/medilens-ai-ml-engineer/scripts/eval_extraction.py
    with (out / "gold.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            row = {k: r[k] for k in ("doc_id", "unit", "quality", "fields")}
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    recs = generate(a.out, a.seed, not a.no_images)
    print(f"wrote {len(recs)} records to {a.out}")


if __name__ == "__main__":
    main()
