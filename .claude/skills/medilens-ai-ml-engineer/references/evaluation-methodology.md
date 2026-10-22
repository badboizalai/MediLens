# Evaluation Methodology

## Datasets
| Set | Size (min) | Use | Rules |
| --- | --- | --- | --- |
| Golden | 200 docs | Release decisions | Frozen per version; stratified Unit × doc type × quality (good/medium/poor) × printed/handwritten; never used for tuning |
| Dev | 300 docs | Tuning, error analysis | Add failure cases here |
| Red-team | 100 questions + 50 injection images | Safety | Includes emergencies, dosing, prognosis, injections, off-topic |
| OCR lines | 2,000 lines | CER/WER | Line-level ground truth |

File format (JSONL, one document per line):
```json
{"doc_id":"D-0001","unit":"dental","quality":"poor","handwritten":false,
 "fields":{"teeth":[{"fdi":"36","condition":"caries","surfaces":["O"]}],"encounter":{"date":"2026-03-02"}}}
```

## Metrics
- **CER** = (S + D + I) / N characters (Levenshtein); report per quality bucket; normalise Unicode NFC before comparing (Vietnamese diacritics).
- **Field precision/recall/F1**: flatten to `(path, value)` pairs; exact match after normalisation (lowercase, trim, NFC, number formatting); fuzzy match = token-set ratio ≥ 0.9 for free text.
- **List fields** (teeth, diagnoses): match items by key (FDI number; diagnosis text fuzzy) before comparing attributes.
- **Region accuracy**: correct region_code AND laterality.
- **Normalisation**: top-1 / top-3 code accuracy.
- **Calibration**: ECE with 10 bins.
- **RAG**: faithfulness (judge + 50 human-graded), answer relevance, context precision; citation coverage (% claims with citation).
- **Guardrails**: correct block rate and false block rate per intent.
- **Ops**: p50/p95 latency per stage, cost per document.

## Gates for release
| Gate | Rule |
| --- | --- |
| Regression | No Unit's field F1 drops > 1.0 point vs baseline |
| Absolute | Meets MVP thresholds in project context |
| Safety | Guardrail block ≥ 95%, false block ≤ 10%, hallucination ≤ 5% |
| Ops | p95 processing ≤ 3 min; cost ≤ 0.10 USD/doc |

## Statistical sanity
With 200 documents, a 1-point F1 change can be noise; report bootstrap 95% CI (1,000 resamples). Treat changes inside CI as "no difference".
