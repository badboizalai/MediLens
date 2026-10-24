# Evaluation report v1 (S11-T108, D108)

Date: 2026-10-24. Owner: ai-ml-engineer. Data: 100 % synthetic. **No LLM was called and no model
prediction exists in the repo**, so every metric that needs a model is reported as *not measurable
yet*. Nothing below is estimated or extrapolated. Thresholds are the MVP column of plan section 10.1
(`docs/plan/project-plan.en.md`, AI metric table).

Status legend: **measured** = computed by a committed command on synthetic data; **n/m** = not
measurable, needs model predictions; pass/fail is only given for measured rows.

## 1. G2 metrics at a glance

| Metric (plan 10.1) | Threshold | Value | n | Status | Result |
| --- | --- | --- | --- | --- | --- |
| Field F1, overall (golden-v2) | >= 0.80 | - | 600 docs | n/m: needs predictions | n.a. |
| Field F1 per Unit: dental / cardiology / oncology | >= 0.80 each | - | 200 docs each | n/m | n.a. |
| Field F1 per stratum (lang, noise, layout, Unit x stratum) | >= 0.80 (project choice for strata) | - | see 600-doc counts below | n/m | n.a. |
| ECE of field confidence | <= 0.10 | - | - | n/m (metric implemented and tested, see 3) | n.a. |
| Error rate among conf >= 0.7 | reported, no gate | - | - | n/m | n.a. |
| Region accuracy, end-to-end (extracted region vs gold) | >= 0.85 | - | 1705 gold regions | n/m | n.a. |
| Region accuracy, mapper only on gold location strings | >= 0.85 | 0.910 | 1705 | measured (synthetic, perfect OCR) | **PASS overall**, FAIL for oncology (0.769) |
| Page classification macro-F1 (rules) | >= 0.85 (plan); 0.90 (own target) | 1.000 | 180 pages | measured (clean synthetic text) | PASS, optimistic |
| LOINC top-1 (normaliser; ICD-10 not evaluable, LIC-002 not approved) | >= 0.85 (own target; plan ICD-10 top-1 >= 0.75) | 0.908 | 153 labelled + 22 refusals | measured | PASS (LOINC only) |
| Guardrails: unsafe blocked / benign false-blocked | >= 95 % / <= 10 % | 100/100 / 0/30 | 130 questions | measured (rules-level red-team) | PASS |
| Prompt-injection defences | no data leak / no obeyed injection | 50/50 caught | 50 PNG manifests (OCR text stood in) | measured | PASS |
| Printed OCR CER (VI/EN) | <= 5 % | paddle 15.63 %, vietocr 4.40 % | 85 pages (golden-v0) | measured (other dataset, see report) | vietocr PASS, paddle FAIL |
| Citation validity | >= 0.95 (project choice) | - | - | n/m | n.a. |
| Tooth number (FDI) accuracy | >= 0.90 | - | - | n/m (extraction needs predictions) | n.a. |
| Faithfulness / hallucination (RAG) | >= 0.85 / <= 5 % | - | - | out of scope of this report | n.a. |

## 2. Extraction harness on golden-v2

Command (run today):

```
cd ml/eval/extraction && python3 -m extraction_eval run --gold ../golden-v2/gold.jsonl
```

Output: `no predictions for 600 gold docs in ../golden-v2/gold.jsonl: F1 not computed (no model results yet)`
(exit 0). The harness refuses to score the CI baseline against v2; `baseline/predictions.jsonl`
is `NOT_A_MODEL_RESULT` and covers golden-v1 only.

Strata that the report will contain once predictions exist (counts from `golden-v2/manifest.json`):

| Group | n docs |
| --- | --- |
| unit=dental / cardiology / oncology | 200 / 200 / 200 |
| lang=vi / en | 420 / 180 |
| noise=clean / light / heavy | 300 / 210 / 90 |
| layout=outpatient_form / discharge_summary / dental_record / lab_result / pathology_report | 200 / 200 / 67 / 66 / 67 |
| lang x unit, noise x unit, layout x unit | emitted as `lang=vi@unit=oncology` etc. |

## 3. New metrics (this task)

Implemented in `ml/eval/extraction/extraction_eval/metrics.py`, tests in `tests/test_metrics.py`
(hand-computed ECE, over-confident wrong fields, empty input, region by unit, gate):

- **ECE**: 10 equal-width bins over every predicted field that has a stated `confidence` (wrapped
  leaf values and `region.region_code`); correct = equals gold at the same path, a field absent
  from gold counts as wrong. Reported overall and per Unit (`calibration` in `report.json`, with
  reliability bins `lo, hi, n, mean_conf, accuracy`) plus the error rate among conf >= 0.7.
  Returns `null`, never 0, when no confidences exist. The gate fails on ECE > `ece_max` (0.10 in
  `thresholds.json`) only when ECE is defined.
- **Region accuracy by unit** (`region_accuracy_by_unit`) next to the existing overall value.
- Plumbing check: running the golden-v1 CI baseline prints ECE 0.062 (n=2096). That number is
  meaningless as model quality: the baseline injects errors without lowering confidence. It only
  shows the code path works.

## 4. Anatomy mapper on golden-v2 gold locations (measured)

Command (`run_eval.py` is the older golden-v1 run):

```
uv run --project apps/worker python ml/eval/anatomy/run_eval_v2.py   # writes ml/eval/anatomy/results_v2.json
```

Input = the gold source quote of every located item (tooth FDI quote, `site`, node `station`), unit
from the record; target = gold `region.region_code`. This is the rules mapper with perfect OCR and
perfect extraction, so it is an upper bound for end-to-end region accuracy.

| Group | Accuracy | n | Threshold 0.85 |
| --- | --- | --- | --- |
| ALL | 0.910 | 1705 | pass |
| dental (teeth) | 1.000 | 785 | pass |
| cardiology (diagnoses site) | 0.926 | 380 | pass |
| oncology | 0.769 | 540 | **fail** |
| oncology primary | 0.870 | 200 | pass |
| oncology metastases | 0.767 | 159 | fail |
| oncology nodes | 0.657 | 181 | fail |
| lang=vi / lang=en | 0.936 / 0.850 | 1190 / 515 | pass / at threshold |
| layout=pathology_report | 0.790 | 167 | fail |

The `noise=` rows in `results_v2.json` are not meaningful here: the input is the clean gold quote,
not the noisy `docs.jsonl` text.

Main errors (153 total, all synonym-table gaps, not logic bugs): `Thất trái` -> none (28),
`Tụy` -> none (26), `Xương sống` -> `bone_sites` instead of `bone_spine` (22), `Para-aortic` ->
`aorta` instead of `ln_paraaortic` (15), English/side-qualified node stations (`Cervical right`,
`Iliac left`, `Hilar left`, `Axillary right`, `Mediastinal`) -> none (~45), `Spine bone`/`Pelvic bone`
variants (15). Fixing `location-synonyms.v1.yaml` is outside this task and is the first next step.

## 5. Other components that can run today (measured, synthetic)

| Component | Command | Result | Source report |
| --- | --- | --- | --- |
| Page classifier (rules) | `uv run --project apps/worker python ml/eval/classify/run_eval.py` | macro-F1 1.000, accuracy 1.000, 180 pages; 6 below the LLM-fallback threshold | `ml/eval/classify/REPORT.md` |
| LOINC normaliser | `uv run --project apps/worker python ml/eval/normalise/run_eval.py` | top-1 0.908 (139/153), precision when answered 1.000, refusals 22/22 | `ml/eval/normalise/REPORT.md` |
| Red-team gate | `uv run pytest -q tests/redteam` | all pass (100/100 unsafe, 0/30 false blocks, 50/50 injections) | `tests/redteam/REPORT.md` |
| OCR bake-off (golden-v0, not v2) | recorded, not re-run (needs engines installed) | CER paddle 15.63 %, vietocr 4.40 %; llm-vision not run | `ml/eval/ocr_bakeoff/REPORT.md` |

Re-run results matched the committed reports (the reports were not rewritten).

## 6. Limitations

- Synthetic, template-based text: labels are the generator's templates; value and co-occurrence
  distributions are not clinical. Classifier 1.000 and mapper dental 1.000 reflect clean templates.
- One-page plain-text documents; no images, tables, stamps or handwriting. `noise` is
  character-level damage (accent loss, glyph confusions), not real OCR output. No real-OCR evidence
  for extraction exists yet (D55 gap).
- The golden-v2 gold carries `confidence = 1.0` on every field; ECE is computed on *predicted*
  confidences only and will need real predictions plus enough samples per bin (n per Unit is
  roughly 2k to 4k fields, but bins above 0.9 will dominate).
- Gold human spot-check (30 docs) and CSO review of oncology wording are still pending
  (`DATASET_CARD.md`). Do not train on golden-v2.
- Mapper accuracy is an upper bound; the end-to-end figure also includes OCR and extraction errors.
- ICD-10 is not evaluated (LIC-002), FDI/tooth-number extraction accuracy is not measurable until
  predictions exist, and RAG faithfulness is out of scope here.

## 7. Next steps for the owner

1. Run the extraction pipeline over `ml/eval/golden-v2/docs.jsonl` (`text` field, noisy; `text_clean`
   for an upper bound) with Bedrock credentials via the AI Gateway, and write one JSON record per
   line: `{"doc_id", "unit", "fields": {...}}` with values wrapped as
   `{"value", "confidence", "source": {"page", "quote"}}` and `region.region_code` + confidence.
   No committed script produces this file yet; it is the missing piece (a thin driver over
   `medilens_worker.extraction`).
2. Score it, which fills every n/m row above, including ECE with reliability bins:

   ```
   cd ml/eval/extraction && python3 -m extraction_eval run \
     --gold ../golden-v2/gold.jsonl --pred <predictions.jsonl> --out-dir out
   ```

   Exit code 1 means a gate failed (F1 overall/per Unit, region, ECE, citation validity).
3. Fix mapper synonym gaps listed in 4, re-run `run_eval_v2.py`, target oncology >= 0.85.
4. Add real-OCR text (golden-v1 images or bake-off output) as a second prediction run to quantify
   the OCR-noise gap, and a human-checked slice before any claim leaves the repo.
