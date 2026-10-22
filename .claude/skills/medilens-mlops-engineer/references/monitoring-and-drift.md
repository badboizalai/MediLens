# Monitoring and drift

| Metric | Target / alert | Owner |
| --- | --- | --- |
| USD per document (7-day avg) | ≤ 0.03 target; alert > 1.5× baseline | MLOps |
| USD per day vs budget | alert at 80% and 100% | MLOps / DevOps |
| Escalation to Tier L | ≤ 15%; alert > 20% | MLOps / AI |
| Cache hit (fixed prompt parts) | ≥ 60% | MLOps |
| Schema failure rate | ≤ 1%; alert > 2% | AI |
| Guardrail block rate / false blocks | ≥ 95% on red-team / ≤ 10% | AI / CSO |
| p95 latency per step | per NFR-04 | SRE |
| Correction rate per field (drift proxy) | alert +5 points week over week | AI / DE |
| Document mix and image quality | alert > 20% shift | DE / DC |
| Provider errors / throttling | alert on breaker open | SRE |

Every alert links to a runbook (SRE skill). Weekly cost review is in the Recurring sheet of the sprint plan.
