# Dataset Card — golden-v1 v1.0.0

| Field | Value |
| --- | --- |
| Purpose | golden (extraction/OCR evaluation, 50 docs per Unit; supersedes golden-v0 smoke set for regression) |
| Size | 150 records (150 ground-truth JSON), 255 JPEG pages (150 clean + 75 degraded + 15 handwriting + 15 perspective), 20 MB (limit 30 MB) |
| Created | 2026-10-23 |
| Location | this directory (git); regenerate with the command below |
| Synthetic | yes (100%) |
| Licence(s) | Own work (MediLens project); no third-party data or templates |
| Contains personal data | no (synthetic): fictional names ("Nguyễn Văn Test"), birth years 1900–1950, fictional facility "Bệnh viện Thử Nghiệm" |
| Schemas | `ml/schemas/*.v1.json` (source page/quote/bbox, confidence, `region`); all 150 records validate |

## Composition
| Unit | Records | Quality good / medium / poor |
| --- | --- | --- |
| dental | 50 | see `quality` in `records/*.json` |
| cardiology | 50 | idem |
| oncology | 50 | idem |

Totals: 150 records, 120 VI / 30 EN (every 5th record is EN), quality 75 good / 53 medium / 22 poor (50/35/15 %), 1 page each. 30 records (20 %) have an extra variant (15 `handwriting`, 15 `perspective`). Handwritten fields: simulated only. Region coverage: dental teeth carry `tooth_<FDI>`; liver metastases carry `liver`; all other `region.region_code` are `null` (unmapped) by design.

## Creation process
- Generator `synth_gen` profile `v1` (version 0.3.0) in `ml/datasets/synth/`, seed `20261001` (golden-v0 used `20260101`), doc ids `gv1-NNN-<unit>-<lang>`. Same seed gives identical output (same Pillow/font environment). Content, rendering and degradations are unchanged from golden-v0 (see its card); the only additions are the `region` objects.
- Ground truth is emitted together with the rendered text, so labels match the image by construction. `gold.jsonl` is in the format of `eval_extraction.py`.
- Labelling guideline: none (generated). Inter-annotator agreement: n/a. Human spot-check of 5 % (8 records) still to be done by the data-curator.
- Leakage check vs golden-v0 (`leakage_check.py`, bytes and `--text` modes): 406 vs 141 files, overlap 0, PASS.

Regenerate:
```
cd ml/datasets/synth && uv run --with pillow python -m synth_gen.generate --profile v1 --out ../../eval/golden-v1
```

## Known biases and gaps
- Same single-layout-per-Unit templates as v0: much cleaner and less varied than real records; expect an optimistic synthetic-to-real gap.
- Handwriting is typeface jitter; perspective is a flat warp; no stamps, two-column layouts or page curl.
- Random draws, no inter-field clinical coherence beyond the TNM-to-stage table and "metastases only when M1".
- `bbox` is not populated (renderer does not emit layout); region mapping is sparse (see above), so region accuracy cannot yet be measured on cardiology or most oncology items.
- 50 per Unit is still modest for per-field F1 confidence intervals; report with intervals.
- No treatment, dosing or prognosis text (BR-042).

## Allowed uses / prohibited uses
- Allowed: internal evaluation of OCR/extraction/pipeline regressions; testing schemas and viewers.
- Prohibited: training or fine-tuning for release models, clinical claims, presenting as real patient data, mixing with real data in a way that hides provenance.

## Maintenance
Owner: ai-ml-engineer; reviewers: data-curator, clinical-informaticist (region codes). Template or seed changes bump generator version and this card; schema changes add `*.v2.json`.
