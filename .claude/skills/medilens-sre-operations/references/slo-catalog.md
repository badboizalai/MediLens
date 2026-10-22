# SLO Catalog (30-day rolling window)

| SLO | SLI (good ÷ valid) | Target | Error budget / 30 d | Source |
| --- | --- | --- | --- | --- |
| API availability | non-5xx responses ÷ all API responses (excluding 4xx from client errors) | 99.5% | 0.5% of requests (~3h36m full outage equivalent) | ALB metrics |
| API latency | read requests < 300 ms ÷ read requests | 95% | 5% | ALB TargetResponseTime / X-Ray |
| Document processing | documents reaching `extracted`/`rejected` within 2 min ÷ documents completed upload | 95% | 5% | app metric |
| Pipeline success | documents not ending `failed` ÷ documents processed | 99% | 1% | app metric |
| Explain availability | explanation requests answered (incl. safe refusals) without error ÷ requests | 99% | 1% | app metric |
| Login success | successful auth flows ÷ attempts with valid credentials | 99.5% | 0.5% | Cognito + app |
| AI Gateway availability | gateway calls answered (incl. budget/quota refusals) without 5xx ÷ calls | 99.5% | 0.5% | gateway metric |
| AI cost guardrail | days with spend ≤ daily budget ÷ days | 100% | 0 (alert at 80%) | gateway metric + AWS Budgets |
| CT processing (v2) | CT cases meshed within 30 min of upload ÷ cases | 90% | 10% | imaging worker metric |
| Support first response (after launch) | tickets answered within SLA ÷ tickets | 95% | 5% | support tool (support-success skill) |

## Burn-rate alerts (multi-window)
| Severity | Burn rate | Long window | Short window | Meaning |
| --- | --- | --- | --- | --- |
| Page (SEV2) | 14.4× | 1 h | 5 min | 2% of monthly budget in 1 h |
| Page (SEV2) | 6× | 6 h | 30 min | 5% in 6 h |
| Ticket (SEV3) | 1× | 3 d | 6 h | on track to exhaust |

## Error budget policy
Budget > 50% left: normal delivery. 0–50%: prioritise reliability items. Exhausted: freeze Normal changes except reliability/security fixes until back within target.
