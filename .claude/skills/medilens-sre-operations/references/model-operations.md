# AI Model Operations in Production

| Signal | Metric | Alert |
| --- | --- | --- |
| Quality proxy | Field correction rate per Unit/model version | +20% week-over-week |
| Calibration drift | Share of fields with confidence < 0.7 | ±20% WoW |
| Mapping | Unmapped rate | +50% WoW |
| Safety | Guardrail trigger rate; emergency intents | spike 3× baseline |
| Latency | p95 per stage | > SLO |
| Cost | USD per document | > 0.10 |
| Provider | Throttling/errors | > 5% for 10 min |

## Release ladder
shadow (no user impact) → canary 10% (AppConfig) → 50% → 100%; each step ≥ 24 h with metrics compared to control; rollback = flag flip.

## Deprecations
Subscribe to provider deprecation notices; plan migration ≥ 30 days ahead; keep `model_version` per run for reproducibility.
