# Multimodal inputs (plan section 26)

All inputs end in one **Finding Graph**: each finding has `sourceType` (record · patient_reported · image_derived), `precision` (exact · segment · organ · system · body_part; confidence < 0.6 → `unmapped`), source reference and confidence.

| Input | Pipeline | Notes | Owner(s) |
| --- | --- | --- | --- |
| Photo of a record | validate → preprocess → classify → OCR (PaddleOCR/VietOCR; LLM vision on low-confidence handwriting crops) → extract → normalise → map | Citations as page + bbox | AI |
| Digital record (text-layer PDF, DOCX) | detect text layer → (OCR only for image pages) → extract → normalise → map | BR-045: no OCR when text exists; citations as page + character offsets | AI + Clinical Informaticist |
| FHIR R4 Bundle | `fhir_bundle_check.py` → deterministic mapping (no LLM) | Identity fields dropped at the PHI boundary | Clinical Informaticist + BE |
| Patient text description | emergency detector first (BR-041) → NER (Tier S) → region mapping → `patient_reported` findings | BR-040: no ICD code, no severity colour, "you described" label | AI + CSO |
| CT series (v2) | de-ID → segmentation → mesh → registration (imaging skill); CT radiology report text → extraction like a digital record | BR-042: anatomy only; findings come from the report text, not from pixels | Medical Imaging + AI |

## Emergency detector (patient text)
High-recall rules + small classifier for chest pain, difficulty breathing, stroke signs, heavy bleeding, suicidal statements, loss of consciousness, severe allergic reaction; accent-insensitive Vietnamese (e.g., "dau nguc" = "đau ngực") and English; on trigger show 115 first and stop other processing for that message. Test set ≥ 200 sentences incl. negatives; recall target ≥ 0.98.

## Conflict handling (BR-044)
Same region + overlapping time window + contradicting statements → keep both, rank record > image_derived > patient_reported, show a mismatch warning naming the sources.

## Evaluation additions
- Digital records: field F1 on text-layer PDFs separately from photos.
- Patient text: entity F1 and region accuracy on 300 sentences; emergency recall.
- CT report extraction: F1 on 30–50 synthetic/public reports.
