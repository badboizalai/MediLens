# Pipeline Spec — <name>

| Field | Value |
| --- | --- |
| Owner | data-engineer |
| Source → Target | |
| Schedule / trigger | |
| SLA | finished by HH:MM ICT |
| Idempotency key | e.g. `dt` partition |
| Data classes in / out | C4 → C2 (pseudonymised) |
| Orchestrator | Prefect / Dagster / EventBridge Scheduler |

## Steps
1.
## Data quality checks
| Check | Rule | On failure |
| --- | --- | --- |
## Alerts
- Failure → <channel>; not finished by SLA → dead-man alert
## Backfill procedure
## Lineage / catalog updates
## Cost estimate (Athena bytes, compute minutes)
