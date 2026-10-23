# Dataset Card — golden-v2 v2.0.0

| Field | Value |
| --- | --- |
| Purpose | Per-Unit extraction golden set (D76 dental, D86 cardiology, D92 oncology incl. TNM/primary/nodes/metastases); feeds the D108 per-Unit F1 report |
| Tier and sources | Tier 1 synthetic; no external source (no LIC entry needed) |
| Licence | Own work (MediLens project), released CC0 for internal use; no third-party text or templates |
| Consent basis | own work (100 % generated) |
| Size, splits, strata | 600 docs = 200 per Unit (dental, cardiology, oncology); text level, ~1.9 MB (`gold.jsonl` 1.2 MB, `docs.jsonl` 0.7 MB). No train/test split: evaluation only |
| Strata (per record, in `gold.jsonl` `strata`) | `lang` vi 70 % / en 30 % (140/60 per Unit); `noise` clean 50 % / light 35 % / heavy 15 % (100/70/30 per Unit); `layout` = page type from `synth_gen.pages` (3 per Unit, ~1/3 each). Every lang x noise cell is populated per Unit |
| Label schema | `fields` validate against `ml/schemas/{dental,cardiology,oncology}.v1.json` (+ common): values with page/quote sources, `region.region_code` from `data/terminology/region-tree.v1.yaml`, LOINC hints from the `loinc-*.v1.csv` subsets, FDI from `fdi.csv`. Oncology: primary site/histology/size/grade, T/N/M/stage (AJCC 8, simplified project table, not a staging reference), nodes (incl. explicitly *not involved*), metastases (confirmed/suspected, only when M1) |
| Annotators, agreement | n/a (label = generator template); human spot-check of 5 % (30 docs) still to be done by the data-curator; CSO review of oncology wording pending |
| De-identification | n/a: fictional names ("Nguyễn Văn Test" pattern), birth_year 1900–1950, fictional facility; every text carries `SYNTHETIC - TEST ONLY` |
| Content rules | No ICD-10 codes (LIC-002), no treatment advice, dosing, prognosis or survival statements (BR-042); tests enforce this |
| Known gaps and biases | Template-based; random draws are not real clinical distributions or co-occurrences; one-page, plain-text documents (no images, tables, stamps, bbox); `noise` is character-level OCR-like damage (accent loss, glyph confusions) on `docs.jsonl` `text`, not real OCR output; `layout` changes only the title line, not the geometry; region mapping is exact by construction so region accuracy is optimistic; 200 per Unit still needs confidence intervals per stratum (about 20–70 docs per cell) |
| Allowed / prohibited uses | Allowed: internal regression and per-Unit/stratum F1 of extraction, prompt A/B. Prohibited: training or fine-tuning models that are then scored here, clinical claims, presenting as real data, standing in for real-record evaluation (golden-v1 images and future real-OCR sets remain required) |
| Files | `gold.jsonl` (extraction gold + strata), `docs.jsonl` (model input: `text`, noise-free `text_clean`, patient), `manifest.json` (counts, sha256) |
| Regeneration | `cd ml/datasets/synth && python3 -m synth_gen.golden_v2 --out ../../eval/golden-v2` (stdlib only; `--check` verifies the committed copy). Seed `20261024`; a test fails if the committed files differ from a rebuild |
| Scoring | `cd ml/eval/extraction && python3 -m extraction_eval run --gold ../golden-v2/gold.jsonl --pred <model predictions.jsonl>`; reports F1 per Unit, per stratum and per Unit x stratum (`lang=vi@unit=oncology`). Without predictions it prints "no predictions" and computes nothing; there is no baseline for v2 |
| Created by / date / commit | ai-ml-engineer, 2026-10-24, task S8-T76 / S9-T86 / S10-T92 (data part) |
| Models using this version | none yet |
| Retention | repository lifetime (synthetic) |
