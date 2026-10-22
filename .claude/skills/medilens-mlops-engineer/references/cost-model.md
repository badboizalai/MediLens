# Cost model

## Formula (per document)
cost_doc = Σ_steps r_s × [(T_in_new × P_in + T_in_cached × P_cache + T_out × P_out)_tier(s)] + GPU_sec × P_gpu_sec
where r_s is the share of documents that pass through step s.

## Worked example (plan 28.4; prices are illustrative assumptions)
Tier S 0.15 / 0.15 USD per million tokens in/out; Tier M 1 / 5; Tier L 3 / 15; cache read = 10% of input price. Three-page document, ~2,500 OCR tokens.
| Step | Tier | Share | Tokens new / cached / out | USD |
| --- | --- | --- | --- | --- |
| Page classification | S | 100% | 600 / 0 / 20 | 0.000093 |
| Extraction | M | 100% | 2,500 / 1,500 / 800 | 0.00665 |
| Mapping 5 findings | S | 100% | 1,000 / 0 / 100 | 0.000165 |
| Escalation | L | 12% | 4,000 / 0 / 800 | 0.00288 |
| **Total** | | | | **≈ 0.0098** |
One explanation question (Tier M, 1,000 new / 2,000 cached / 300 out) ≈ 0.0027 USD. 100 users × 5 documents + 20 questions per month ≈ 4.9 + 5.4 ≈ 10 USD/month in tokens. `scripts/cost_model.py assets/cost-model-example.json` reproduces these numbers.

## Levers (plan 28.3)
Batch inference (about 50% cheaper than on-demand for supported models) for evals, reprocessing and synthetic data · prompt caching (cache reads much cheaper than fresh input; writes slightly dearer) · flex/priority service tiers where the provider offers them · cascade with escalation ≤ 15% · result cache for duplicate documents · fewer input tokens (drop repeated headers/footers, only clinical pages) · output limits · quotas and budgets · distillation.

## Self-host break-even
A GPU at an assumed 1 USD/hour running all month ≈ 720 USD. Break-even ≈ 720 / 0.0098 ≈ 73,000 documents/month before operations effort. At personal-project scale, pay-per-token is far cheaper; self-host for learning or as batch jobs that scale to zero.
