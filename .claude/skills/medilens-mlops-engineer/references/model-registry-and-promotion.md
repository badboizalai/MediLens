# Model registry and promotion

## Registry entry (MC-xxx)
provider · model id (pinned) · region · tier · task(s) · prompt version · schema version · thresholds · eval results (golden, per Unit, per subgroup) · cost/latency · datasets (DS ids) · AI impact assessment id · status (candidate, shadow, canary, live, retired) · owner · dates.

## Stages
candidate → shadow (100% traffic mirrored, outputs not shown, 7 days) → canary (10% via AppConfig) → live → retired (kept for audit and rollback).

## Rollback criteria (any one)
F1 proxy (correction rate) worse by > 2 points · schema failures > 2% · p95 latency > target for 1 hour · cost/document > 1.5× baseline · any guardrail regression · safety report class A.

## Quarterly bake-off
2–3 candidates per tier on the golden set; compare F1, latency, cost; write ADR; update Model Cards. Also triggered by provider deprecation notices.
