# Cascade routing

## Tiers
Rule/cache (0 tokens) → Tier S (small, cheapest) → Tier M (mid, structured output + vision) → Tier L (large, hard cases) → human review (user confirmation already required by BR-012).

## Task assignment (plan 28.1)
| Task | Default | Escalation |
| --- | --- | --- |
| Image quality | OpenCV rules | — |
| Printed OCR | PaddleOCR/VietOCR self-hosted | LLM vision on low-confidence crops |
| Handwriting | Tier M vision on crops only | Tier L |
| Page classification | keywords + Tier S | Tier M |
| Field extraction | Tier M structured output | Tier L when confidence < threshold or schema fails twice |
| Code normalisation | dictionary → embedding kNN → Tier S chooses among top-5 | Tier M |
| Region mapping | rules → Tier S chooses from the Unit's closed list | Tier M |
| Text NER (patient_reported) | Tier S | Tier M |
| Explanations (RAG) | Tier M, ≤ 250 words | — |
| Intent guardrail | rules + Tier S, before any larger call | block |
| Offline judge, synthetic generation | Tier L in batch | — |
| CT segmentation | TotalSegmentator on GPU | — |

## Thresholds
Confidence = calibrated combination of model-reported confidence, schema validity, agreement with rules, and OCR confidence of cited spans. Calibrate on the dev set (ECE ≤ 0.05), pick thresholds with `threshold_tuner.py`, store them in the router config, and re-tune after every model/prompt change.

## Rules
- Escalate at most once per document per step; then `needs_review`.
- Never escalate guardrail-blocked content to a bigger model.
- Track escalation rate per Unit and document type; > 15% means fix the Tier M prompt/schema, not accept the cost.
