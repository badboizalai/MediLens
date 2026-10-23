# Page classifier (rules) - 9-type synthetic set, `test` split

- Pages: 180 (20 per type, seed 20261023, text-level, VI/EN)
- Macro-F1: **1.000** (target >= 0.9); accuracy 1.000
- Below LLM fallback threshold (0.5): 6

## Per-type

| type | support | precision | recall | F1 |
|---|---|---|---|---|
| discharge_summary | 20 | 1.000 | 1.000 | 1.000 |
| outpatient_form | 20 | 1.000 | 1.000 | 1.000 |
| lab_result | 20 | 1.000 | 1.000 | 1.000 |
| pathology_report | 20 | 1.000 | 1.000 | 1.000 |
| imaging_report | 20 | 1.000 | 1.000 | 1.000 |
| dental_record | 20 | 1.000 | 1.000 | 1.000 |
| prescription | 20 | 1.000 | 1.000 | 1.000 |
| order_form | 20 | 1.000 | 1.000 | 1.000 |
| other | 20 | 1.000 | 1.000 | 1.000 |

## Confusion matrix (rows = true, columns = predicted)

| true \ pred | discharge_summary | outpatient_form | lab_result | pathology_report | imaging_report | dental_record | prescription | order_form | other | unknown |
|---|---|---|---|---|---|---|---|---|---|---|
| discharge_summary | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| outpatient_form | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lab_result | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| pathology_report | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| imaging_report | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 |
| dental_record | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 |
| prescription | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 |
| order_form | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 |
| other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |

## Misclassified ids

- none

## Before / after rule changes (macro-F1)

Changes made on `dev` only: title-line bonus (strong match in first 2 lines +2), `other` rules,
`phieu sieu am`. Before: dev 0.827, test 0.861 (lab/imaging/dental false positives from distractor
lines; `other` never predicted). After: dev 1.000, test 1.000.

## Caveats

- 1.000 is optimistic: synthetic templates, clean text, no OCR noise, 4-5 title variants per type,
  written knowing the rule vocabulary. It shows the target is *measurable* and the rules work on
  clean text; it is not evidence for real scans. The old golden-v1 run (2 types) is superseded.
- Real-OCR evidence (D55) is still missing, see below.

## Offline OCR baseline (image -> OCR -> classify): not run

No `tesseract` binary, PaddleOCR or VietOCR is installed here, and none was installed (heavy).
To run it: (1) render page images (`synth_gen`, needs `pillow` and DejaVu Sans); (2) OCR with
PaddleOCR (`paddlepaddle` CPU + `paddleocr`, ~0.5-1 GB of wheels, det+rec weights ~15-30 MB
downloaded on first run) or `apt install tesseract-ocr tesseract-ocr-vie` (~30 MB) +
`pytesseract`; ~1-3 s/page on CPU, ~10 min for 255 pages; (3) feed the text to `classify_text`
and compare macro-F1 with this report. golden-v1 images carry no page-type labels, so the OCR run
needs images rendered from `synth_gen.pages` (that render step is not written yet).
