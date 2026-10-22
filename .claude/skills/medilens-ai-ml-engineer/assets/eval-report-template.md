# AI Evaluation Report — <change name> (<date>)

| Item | Baseline | Candidate |
| --- | --- | --- |
| Pipeline version | | |
| OCR engine | | |
| LLM model ID | | |
| Prompt versions | | |
| Golden set version | | |

## Results
| Metric | Unit | Baseline | Candidate | Δ | 95% CI | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| Field F1 | dental | | | | | ≥ baseline − 1 |
| Field F1 | cardiology | | | | | |
| Field F1 | oncology | | | | | |
| CER printed | all | | | | | ≤ 5% |
| Region accuracy | all | | | | | ≥ 0.85 |
| ICD-10 top-1 | all | | | | | ≥ 0.75 |
| Faithfulness (RAG) | all | | | | | ≥ 0.85 |
| Guardrail block / false block | all | | | | | ≥ 95% / ≤ 10% |
| p95 processing time | all | | | | | ≤ 3 min |
| Cost per document (USD) | all | | | | | ≤ 0.10 |

## Error analysis (top buckets)
| Bucket | Count | Example | Planned fix |
| --- | --- | --- | --- |

## Decision
GO / NO-GO — rationale. Rollout plan: shadow → 10% → 100%. Rollback trigger:
