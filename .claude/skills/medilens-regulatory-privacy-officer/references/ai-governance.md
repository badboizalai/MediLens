# AI governance policy (MediLens)

## Policy statements
1. AI in MediLens extracts, normalises, maps and explains information from the user's own records; it never makes clinical decisions.
2. Every AI output that reaches the viewer is confirmed by the user (BR-012/013) and shows its source.
3. Every model, prompt or provider change goes through PB-03 with evaluation, an AI impact assessment when the use case or data changes, and a rollback plan.
4. No user data is used for training without separate opt-in consent (BR-034) and a dataset that passed G1-D.
5. Providers must not train on MediLens data and must document retention and region.

## Risk tiering
| Tier | Use | Extra controls |
| --- | --- | --- |
| Low | Page classification, OCR | Eval gate |
| Medium | Field extraction, code normalisation, anatomical mapping | Eval gate per Unit + subgroup bias check + user confirmation |
| High | Free-text explanations (RAG), CT-derived anatomy | Guardrails, red-team in CI, CSO content review, monitoring of refusals and complaints |

## Transparency
Users see: that AI is used, what it does, its limits, and how to correct results. Model Cards (MLOps) record version, data, metrics, known limitations.

## Human oversight
User confirmation for every extracted field; CSO review for content; QC release gate; kill switch per AI feature via AppConfig.

## Bias and fairness checks
Report metrics by subgroup: handwritten vs printed, photo quality, Vietnamese vs English, Unit, document type, age group (adult/child). Gap > 5 points F1 → mitigation before release.
