# Data sourcing playbook

## Tiers (move up only after the previous gate)
| Tier | Source | Gate before use | Typical use |
| --- | --- | --- | --- |
| 1 | Synthetic records generated from Unit templates (LLM text → HTML forms → images with blur/skew/fold/stamp/handwriting-font variants) | Dataset Card | Dev, golden set core, CI |
| 2 | Public datasets with suitable licences | License Register decision, G1-D | Evaluation, CV/segmentation reference, pre-training |
| 3 | Opt-in user donations (consent C3) | G3-P passed, donation pipeline, de-identification QA | Real-world evaluation and drift; later fine-tuning |
| 4 | Partner hospitals | DSA + partner ethics approval + DPIA/OTIA | Large-scale realistic data |

## Needs per AI component (summary of plan table 25.1)
| Component | Evaluation minimum | Training (only if needed) |
| --- | --- | --- |
| Image quality check | 300 images good/bad | thresholds, no training |
| Page classification | 30 per type (≈ 270) | 200–500 per type |
| Vietnamese OCR | 2,000 lines | 10k+ lines to fine-tune VietOCR |
| Field extraction | 200 documents per Unit | 1,000–3,000 per Unit to distil a small model |
| Code normalisation | 500 term→code pairs | dictionary + embeddings |
| Anatomical mapping | 300 phrases per Unit | rules + LLM |
| RAG explanations | 200 questions + 100 red-team | none |
| Text descriptions | 300 sentences | none in v1 |
| CT (v2) | 30–50 reference cases | pre-trained TotalSegmentator |

## Sourcing steps
1. Write the need (component, labels, size, strata).
2. Search candidates; for each, read the licence/DUA and add a register row (decision pending).
3. Regulatory review for anything with NC, SA, DUA or unclear terms.
4. Download only after a positive decision; store checksum and source URL.
5. Create the Dataset Card; register version; run leakage check against the golden set.

## Paid creation (tier 1.5)
Clinicians or medical students write realistic but fictional records (200–500 per Unit) under a contract that assigns rights to the project and forbids using real patients' details.
