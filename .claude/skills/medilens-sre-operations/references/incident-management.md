# Incident Management

| SEV | Definition | Response | Updates |
| --- | --- | --- | --- |
| SEV1 | Data exposure or full outage | Immediate | every 30 min |
| SEV2 | Core feature broken for many (upload/processing/viewer/login) | ≤ 1 h | every 60 min |
| SEV3 | Partial degradation with workaround | ≤ 1 business day | daily |
| SEV4 | Minor/cosmetic | next sprint | — |

## Steps
1. **Declare**: create incident doc (time UTC, SEV, symptoms, dashboards).
2. **Roles** (solo: you hold all, but write them): Incident Commander, Ops, Comms, Scribe.
3. **Stabilise**: rollback last deploy / disable flag / scale / pause consumers / block client in WAF.
4. **Communicate**: status page / in-app banner with plain message; no internal details.
5. **Diagnose**: traceId → X-Ray → logs; recent changes (deploy, config, provider status).
6. **Resolve & verify**: SLI back to normal for 30 min.
7. **Close**: post-mortem scheduled (SEV1–2 within 48 h).

## Common playbooks
- Provider outage (Bedrock/OCR): circuit breaker open → keep jobs queued with delay; banner "processing slower than usual".
- DB overload: identify top queries (Performance Insights), kill runaway, scale instance class, add index via hotfix.
- Poison messages: inspect DLQ sample (IDs only), fix, redrive.
- Bad deploy: redeploy previous task definition; migrations are backward compatible so code rollback is safe.
