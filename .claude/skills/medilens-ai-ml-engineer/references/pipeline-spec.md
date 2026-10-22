# AI Pipeline Specification

## Contents
1. Stage contracts
2. Thresholds and defaults
3. Persistence and replay
4. Confidence model
5. Failure handling

## 1. Stage contracts
| Stage | Input | Output | Key logic | Timeout / retries | Metric |
| --- | --- | --- | --- | --- | --- |
| validate | S3 object key | `{ok, pages[], reasons[]}` | magic bytes, size, page count, malware result, blur (variance of Laplacian), resolution | 60 s / 3 | rejection precision/recall |
| preprocess | page images | normalised page images | document edge detection + perspective warp, deskew (Hough/minAreaRect), denoise, CLAHE contrast, max side 2480 px | 120 s / 3 | downstream CER delta |
| classify | page image (+ quick OCR) | `{doc_type, confidence}` | zero-shot vision LLM → small classifier later | 60 s / 3 | macro-F1 |
| ocr | page image | `{lines:[{text, bbox, conf}], lang}` | PaddleOCR (det + rec) + VietOCR for VI printed lines; Bedrock vision for low-confidence/handwritten regions; Textract only if language = en | 300 s / 3 | CER/WER |
| extract | OCR text (reading order) + doc_type + unit hints | JSON per Unit schema with `{value, confidence, source}` | LLM structured output, temperature 0, schema validation, 1 repair retry | 300 s / 2 | field F1 |
| normalise | extracted values | codes (ICD-10 top-3, LOINC, UCUM units) | dictionary → embedding kNN → LLM rerank | 60 s / 2 | top-1/top-3 accuracy |
| map | site text + Unit regions | `region_code`, laterality, confidence | rules → constrained LLM choice → unmapped | 60 s / 2 | region accuracy |
| validate_medical | all above | flags, aggregate confidence | rule checks (FDI ranges, dates, sex–organ, units) | 30 s / 3 | % flagged that were truly wrong |
| materialize | user-confirmed fields | Condition, BodyFinding, Observation rows | idempotent upsert, outbox event | 60 s / 5 | — |

## 2. Thresholds and defaults
- Blur: variance of Laplacian < 100 on 1000-px-normalised grayscale → reject (tune on dev set).
- Resolution: short side < 1000 px → reject.
- Field confidence < 0.7 → must confirm (BR-012). Page type confidence < 0.6 → `unknown` (BR-018).
- Mapping confidence < 0.6 → `unmapped` (BR-015).
- Per-document LLM cost cap 0.10 USD (BR-019).

## 3. Persistence and replay
Store intermediate outputs at `s3://<env>-phi-pipeline/<document_id>/<stage>/v<pipeline_version>.json` (KMS, same retention as original). `extraction_runs` records pipeline, model, prompt versions, cost, timings. Replays use stored inputs to compare versions offline.

## 4. Confidence model
Field confidence = min(OCR confidence of quoted span, LLM self-score calibrated, rule-check factor). Calibrate on dev set with isotonic regression; report ECE; never show raw LLM self-confidence uncalibrated.

## 5. Failure handling
| Failure | Behaviour |
| --- | --- |
| Validation fail | status `rejected` + reason code + user tip |
| Provider timeout | retry with backoff; circuit breaker; then requeue with delay |
| Schema invalid twice | `needs_review`, show raw OCR for manual entry |
| Cost cap hit | `needs_manual` (BR-019) |
| Unknown doc type | continue OCR; extraction with generic schema; flag in review |
| Prompt-injection detected in text | strip/ignore instruction-like spans, log security event, continue with extraction only |
