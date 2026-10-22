# Disaster Recovery Plan

## Objectives
RPO ≤ 24 h (target 5 min via RDS PITR) · RTO ≤ 4 h.

## Protected assets
| Asset | Protection | Restore method |
| --- | --- | --- |
| RDS PostgreSQL | Automated backups + PITR 35 d; AWS Backup copies to backup-vault account (vault lock); monthly snapshots 1 y | Restore to new instance at point in time; repoint via Secrets Manager/DNS |
| S3 PHI originals | Versioning; replication (optional, same region different account); Object Lock for audit bucket | Restore previous versions; copy from replica |
| Infrastructure | Terraform in git; state versioned | Re-apply stacks in order |
| Secrets/keys | Secrets Manager; KMS keys with deletion window 30 d | Recreate secrets; never delete CMKs hastily |
| Container images | ECR (immutable tags) + rebuild from git | Redeploy tag |

## Scenarios
1. Accidental table delete/corruption → PITR restore to new instance, extract affected rows, reconcile.
2. Region-wide outage → (learning target) rebuild in second region from backups copied cross-region; accept longer RTO.
3. Ransomware/credential compromise → isolate account, restore from backup-vault (locked), rotate all credentials.
4. Bad migration → roll forward with fix; PITR only if data destroyed.

## Drill procedure (quarterly)
1. Pick a timestamp T; restore RDS to T into isolated VPC in a drill account.
2. Restore a sample of S3 object versions.
3. Run integrity checks (row counts vs metrics at T, checksums, app smoke tests against restored DB with no external access).
4. Record start/end times → achieved RTO; data gap → achieved RPO.
5. Destroy drill resources; record lessons.
