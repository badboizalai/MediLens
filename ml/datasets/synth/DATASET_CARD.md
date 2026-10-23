# Dataset Card — synth-pages-9type v1.0.0

| Field | Value |
| --- | --- |
| Name / purpose | 9-type page-classification set (text level) to measure the page-classifier target (D54, macro-F1 >= 0.90) |
| Tier and sources | Tier 1 synthetic; no external source (no LIC entry needed) |
| Consent basis | own work (100 % generated) |
| Size, splits, strata | 360 pages = 9 types x 40; `dev` (even index, 20/type, rule tuning) and `test` (odd index, 20/type, held out) |
| Label schema | `page_type` = `PageType` values in `apps/worker/src/medilens_worker/classify/page_types.py` (discharge_summary, outpatient_form, lab_result, pathology_report, imaging_report, dental_record, prescription, order_form, other); no guideline (generated) |
| Annotators, agreement | n/a (label = generator template); human spot-check of 5 % still to be done by the data-curator |
| De-identification | n/a: fictional "Nguyen Van Test", birth_year 1900, no real facility |
| Known gaps and biases | Clean text, no OCR noise, no layout; 4-5 title variants per type, VI/EN mix (diacritics always present); 30 % of pages carry one distractor line from another type; titles were written knowing the rule vocabulary, so scores are optimistic and are NOT evidence for real OCR text |
| Allowed / prohibited uses | classifier regression and rule tuning on `dev`; reporting on `test`. Not for training a model that is then scored on `test`; not a substitute for real-OCR evaluation |
| Checksum manifest | none: not committed, regenerated deterministically (`synth_gen.pages.generate_pages(20261023)`) |
| Created by / date / commit | ai-ml-engineer, 2026-10-23, task S6-T54c |
| Models using this version | rules classifier (`classify/rules.py`) |
| Retention | repository lifetime (synthetic) |

Regenerate and score: `python ml/eval/classify/run_eval.py --split test` (see `ml/eval/classify/REPORT.md`).
Image-level golden sets (golden-v0/v1) keep their own cards under `ml/eval/`.
