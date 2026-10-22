# Extraction evaluation harness (S5-T46)

Scores predicted extraction JSON against `ml/eval/golden-v1/gold.jsonl` (synthetic, 150 docs).
Stdlib only. Ported from `.claude/skills/medilens-ai-ml-engineer/scripts/eval_extraction.py`.

Metrics: field-level precision/recall/F1 (exact + fuzzy) overall, per Unit, per quality and per
field path (`teeth[].condition`); region-code accuracy (gold `region.region_code` non-null only);
citation validity (positive page, non-empty quote that occurs in the document's gold quotes on
that page).

Thresholds live in `thresholds.json` (plan section 10.1: field F1 >= 0.80, region accuracy
>= 0.85; citation validity >= 0.95 is a project choice). The gate exits 1 on any regression.

```
cd ml/eval/extraction
python3 -m extraction_eval run --out-dir out            # baseline vs golden-v1, writes report.{md,json}
python3 -m extraction_eval run --pred my_preds.jsonl    # score real predictions
python3 -m extraction_eval gen-baseline [--check]       # regenerate / verify the baseline
uv run --no-project --with pytest pytest                # unit tests
```

## Baseline is NOT a model result

`baseline/predictions.jsonl` is produced by a seeded "oracle-with-noise" generator: ground truth
plus ~4% dropped/corrupted fields, wrong region codes and bad citations. It exists only so CI
exercises scoring and the gate without any LLM call. Each record carries
`_label: NOT_A_MODEL_RESULT...` and reports print the same banner. Do not quote its scores as
extraction quality. Real model predictions replace it once the extraction pipeline emits them.
