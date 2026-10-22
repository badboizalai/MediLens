# Retention Matrix

| Data | Class | Hot | Archive | Delete | Mechanism |
| --- | --- | --- | --- | --- | --- |
| Original images/PDFs | C4 | S3 Intelligent-Tiering until user deletes | auto tiering | soft 0 d, hard 30 d after account deletion | DSR flow + lifecycle on `deleted/` prefix |
| Pipeline intermediates | C4 | 30 d after confirm | — | 30 d | S3 lifecycle |
| OCR text, extraction rows | C4 | RDS while document exists | — | with document | DB cascade |
| Confirmed clinical data | C4 | RDS while account exists | — | with account | DSR flow |
| Incomplete uploads | C4 | 24 h | — | 24 h | S3 lifecycle (abort multipart + prefix rule) |
| Audit events | C2 (no clinical content) | CloudWatch/RDS 90 d | S3 Object Lock 3 y | after 3 y | lifecycle + Object Lock retention |
| App logs | C2 (redacted) | 30 d | S3 1 y | 1 y | CloudWatch retention + export |
| LLM prompt/response logs (redacted) | C2 | 30 d | — | 30 d | Langfuse/CloudWatch retention |
| Analytics (pseudonymised) | C2 | 2 y rolling | — | 2 y | partition drop job |
| DB backups | C4 | PITR 35 d | monthly snapshots 1 y in backup-vault account | 1 y | AWS Backup plan |
| ML datasets (synthetic) | C0 | indefinite | — | on retirement | manual |

Backups cannot be selectively edited: deletion requests are honoured by expiry, or by crypto-shredding the user's data key when application-level encryption is used. Document this in privacy policy and DSR responses.
