# Change Management

| Type | Examples | Requirements | Approval |
| --- | --- | --- | --- |
| Standard | Dependency patch via Renovate, feature deploy through CI, config change within validated AppConfig schema | CI green, automated rollback | Pre-approved |
| Normal | Schema migration, model/prompt change, new AWS resource, IAM change, Unit addition, retention change | RFC (purpose, risk, rollback, tests, schedule, comms) | You as CAB with checklist; security review if data/IAM |
| Emergency | Critical vuln patch, SEV1 fix | Do it, then RFC within 24 h | Post-hoc |

Freeze: no Normal changes when the error budget is exhausted or during an active SEV1–2.
Post-change verification: SLI check at +30 min, +24 h; record outcome (success / rolled back / caused incident) for change failure rate.
