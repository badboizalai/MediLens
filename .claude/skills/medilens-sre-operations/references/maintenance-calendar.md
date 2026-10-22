# Maintenance Calendar

| Frequency | Task | Owner role | Evidence |
| --- | --- | --- | --- |
| Daily (auto) | Backup verify, AI nightly eval, data quality run, cost anomaly check, cron heartbeats | sre / ai-ml / data | alarms green |
| Daily (10 min) | Review SLO dashboard, new Sentry issues, DLQ, GuardDuty findings | sre | daily note |
| Weekly | Merge Renovate dependency PRs, bug triage, AI correction-rate review, cost review, 2-hour maintenance block (small tech debt, runbook updates) | devops / qa / ai-ml | changelog |
| Monthly | Rebuild/patch base images, rotate non-automatic secrets, IAM Access Analyzer review, retention cleanup report, SLO & error budget report, medical content due for review, capacity check | devops / security / sre / qc | monthly ops report |
| Quarterly | DR drill (RDS PITR + S3 restore to isolated account), access review, incident tabletop, provider/model re-evaluation, load test on staging, Well-Architected review, threat model refresh | sre / security / ai-ml / architect | drill & review records |
| Every 6 months | Self-pentest against ASVS, DPIA/privacy policy review | security | reports |
| Yearly | Major version upgrades (PostgreSQL, Python, Node, Next.js), KMS rotation check, architecture & roadmap review, domain/certs renewal check | all | ADRs, release |
