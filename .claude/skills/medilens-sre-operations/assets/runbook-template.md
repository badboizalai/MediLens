# RB-<nn>: <alarm or task name>

| Field | Value |
| --- | --- |
| Trigger | <alarm name / condition> |
| Severity | SEV |
| Owner role | |
| Dashboards | <links> |
| Last tested | YYYY-MM-DD |

## Symptoms and user impact
## Quick checks (≤ 5 min)
1. Recent deploys/config changes? (deploy log, AppConfig history)
2. Provider status (AWS Health, Bedrock)?
3. Key metrics: <list>
## Mitigation
1.
## Verification
SLI back to normal for 30 min; no new errors.
## Escalation
When to hand over to security-engineer (possible PHI exposure) or open SEV1.
## Follow-up
Ticket for root-cause fix; update this runbook.
