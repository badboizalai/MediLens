# Data Requirements Catalog

| Code | Requirement | Strength | Verification |
| --- | --- | --- | --- |
| DAT-01 | Every table/bucket/topic in the catalog with owner, class, description, retention | MUST | Catalog lint in CI (every migration table has entry) |
| DAT-02 | Clinical records trace to document_id + extraction_run_id + page + bbox | MUST | Schema review, test |
| DAT-03 | `ai_value` and `user_value` stored separately; never overwrite | MUST | Unit test |
| DAT-04 | Times `timestamptz` UTC; visit dates `date` | MUST | Migration lint |
| DAT-05 | Units normalised to UCUM, original value + unit kept | MUST | DQ rule |
| DAT-06 | Codes: ICD-10, LOINC, SNOMED/FMA, FDI, TNM with version + valid_from | MUST | Reference load test |
| DAT-07 | Master data only via PR + migration with history | MUST | No manual write grants in prod |
| DAT-08 | Analytics pseudonymised (HMAC key in Secrets Manager); no C3 | MUST | Scan analytics schema for PII columns |
| DAT-09 | Published stats only for groups ≥ 10 | MUST | Dashboard query guard |
| DAT-10 | User data in eval/training only with opt-in, de-identified, documented | MUST | Dataset build filter + card |
| DAT-11 | Expand → migrate → contract schema changes | MUST | Migration review |
| DAT-12 | Backups restorable, verified periodically | MUST | DR drill record |
| DAT-13 | Export in machine-readable format (JSON; FHIR Bundle v2) | SHOULD | E2E |
| DAT-14 | Data contracts for every analytics feed | SHOULD | Contract validation in CI |
| DE-01 | Idempotent pipelines (overwrite by partition) | MUST | Re-run test |
| DE-02 | Owner, schedule, SLA, failure alert, dead-man switch | MUST | Orchestrator config review |
| DE-03 | Pseudonymise before writing Bronze | MUST | Bronze scan |
| DE-04 | Managed schema (Glue Catalog); breaking change fails | MUST | Pipeline test |
| DE-05 | dbt tests on all Silver/Gold models | MUST | CI |
| DE-06 | Documented, ranged backfills without duplicates | MUST | Runbook |
| DE-07 | Column lineage | SHOULD | dbt docs |
| DE-08 | Athena workgroup bytes-scanned limit | SHOULD | Terraform |
| DE-09 | Immutable versioned ML datasets with cards and checksums | MUST | Dataset registry |
| DE-10 | Weekly DQ report to PO + AI | SHOULD | Report |
