# Dataset Card — golden-v0 v0.1.0

| Field | Value |
| --- | --- |
| Purpose | golden (smoke-level extraction/OCR evaluation; not a release gate set) |
| Size | 50 records (50 ground-truth JSON), 85 JPEG pages (50 clean + 25 degraded + 5 handwriting + 5 perspective), ~6.5 MB |
| Created | 2026-10-23 |
| Location | this directory (git); regenerate with the command below |
| Synthetic | yes (100%) |
| Licence(s) | Own work (MediLens project); no third-party data or templates |
| Contains personal data | no (synthetic): fictional names ("Nguyễn Văn Test"), birth years 1900–1950, fictional facility "Bệnh viện Thử Nghiệm" |

## Composition
| Unit | Records | VI | EN | good | medium | poor |
| --- | --- | --- | --- | --- | --- | --- |
| dental | 17 | 14 | 3 | 7 | 8 | 2 |
| cardiology | 17 | 14 | 3 | 6 | 8 | 3 |
| oncology | 16 | 12 | 4 | 12 | 2 | 2 |

Totals: 50 records, 40 VI / 10 EN (every 5th record is EN), quality mix 25 good / 18 medium / 7 poor (50/35/15 %), 1 page each. Exact per-record values are in `records/*.json` (`unit`, `quality`, `metadata.lang`). Handwritten fields: 0 (not covered in v0). Table-heavy layouts: cardiology lab lists only.

## Creation process
- Generator `synth_gen` v0.2.0 in `ml/datasets/synth/`, seed `20260101`; same seed gives identical JSON and JPEG bytes (same Pillow/font environment).
- Content from hand-written per-Unit templates (no LLM): ICD-10 codes, FDI 11–48 teeth, LOINC hints, TNM/stage. Ground truth is emitted together with the rendered text, so labels match the image by construction.
- Rendering: Pillow text with DejaVu Sans (Vietnamese diacritics), 1000×1300 px, JPEG quality 80. "good" = clean page; "medium"/"poor" add a degraded variant (blur σ 0.6–2.0, skew ±7°, and for poor also shadow gradient and fold line); parameters are in `metadata.images[].degradations`. A seeded 10 of 50 records (20 %) also get an extra variant: `handwriting` (5; simulated from DejaVu Sans with per-glyph baseline jitter, rotation ±9°, stroke width and blue ink, since no freely licensed handwriting font is installed) or `perspective` (5; 4-point warp, corners moved inward 1–9 % of page size). Ground truth is unchanged.
- Ground truth validates against `schemas/*.v1.json` (derived from `.claude/skills/medilens-ai-ml-engineer/references/extraction-schemas.md`). `gold.jsonl` is in the format of `scripts/eval_extraction.py`.
- Labelling guideline: none (labels are generated). Inter-annotator agreement: n/a. Human spot-check of 5 % (3 records) still to be done by the data-curator.

Regenerate:
```
cd ml/datasets/synth && uv run --with pillow python -m synth_gen.generate --out ../../eval/golden-v0
```

## Known biases and gaps
- Template-based, one layout per Unit: far cleaner and less varied than real Vietnamese records; expect an optimistic synthetic-to-real gap.
- Handwriting is simulated typeface jitter, not real pen strokes (no cursive joins, no crossed-out text); no stamps or two-column layouts; perspective is a flat 4-point warp without page curl; degradations are mild approximations of phone photos.
- Findings are random draws: no inter-field clinical coherence beyond the TNM-to-stage table and "metastases only when M1".
- Small (50 records): not statistically powered for per-field F1 claims; use for regression smoke tests only.
- Only the permanent dentition, a handful of diagnoses/labs per Unit.
- No treatment, dosing or prognosis text (BR-042); oncology `treatments` hold only past type/date.

## Allowed uses / prohibited uses
- Allowed: internal evaluation of OCR/extraction/pipeline regressions; testing schemas and viewers.
- Prohibited: training or fine-tuning for release models, clinical claims, any presentation as real patient data, mixing with real data in a way that hides provenance.

## Maintenance
Owner: ai-ml-engineer; reviewer: data-curator. Any change to templates or seed bumps the generator version and this card; schema changes add a new `*.v2.json` file (old versions stay). A real-like redacted set (permissioned) is needed later to measure the synthetic-to-real gap.
