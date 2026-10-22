# Data dictionary

Machine-readable source of truth: [`data/catalog/columns.csv`](catalog/columns.csv) (one row per
column). This page explains the conventions. Schema source: `apps/api/migrations/versions/` (initial
schema `0001`, see `docs/architecture/erd.md`). Owner: `medilens-data-engineer`; reviewers:
`medilens-security-engineer`, `medilens-regulatory-privacy-officer`.

## Columns of `columns.csv`

| Column | Values |
| --- | --- |
| `table` | `schema.table`. `phi.*` rows describe the PHI service store and are planned (no migration yet, so the check does not cover them). |
| `column` | Column name. |
| `class` | `C4` PHI, `C3` PII, `C2` internal, `C1` public, `C0` synthetic (project data classes). |
| `category` | `phi`, `pii`, `pseudonymised`, `internal`, `public`. |
| `retention` | Taken from `.claude/skills/medilens-data-engineer/references/retention-matrix.md`. |
| `owner` | Role that answers for the column. |
| `source` | Where the value originates. |
| `export` | Treatment when leaving OLTP for analytics/ML: `hash`, `drop`, `band`, `keep`. |

## Classification rules

- Anything in `clinical` that describes a person's health (OCR text, extracted values, dates, codes, findings, storage keys) is **C4 / phi**. Raw `jsonb` model output and boxes are C4.
- `profile_id`, user/profile foreign keys, `actor_id`, `resource_id` and `external_sub` are **C3**: linkable to a person even without a name. Pseudonymised before export.
- Technical metadata (status, versions, confidence, cost, timestamps, own primary keys) is **C2**.
- Catalogues (`units`, `regions`, `unit_configs`) are **C1**; `region_code` is the contract with assets and viewer.
- `audit.audit_events.ip` and `user_agent` are personal data (C3) although the table has no clinical content; the table as a whole keeps the audit retention.
- `clinical.outbox.payload` is C2 by contract: events carry ids and codes only, never PHI. `export` is `drop` regardless.
- No name, email or phone columns exist in `clinical` (CLAUDE.md). Direct identifiers live only in the PHI service.

## PHI service fields (planned)

| Field | Class | Note |
| --- | --- | --- |
| `phi.identifiers.full_name`, `date_of_birth`, `national_id` | C4 | Direct identifiers; never leave the PHI service. |
| `phi.identifiers.phone`, `email`, `address` | C3 | Dropped in every export. |
| `phi.identifiers.profile_id` | C3 | Join key to `identity.patient_profiles`; pseudonymised for export. |
| `phi.objects.object_key`, `kms_key_id` | C4 / C2 | Metadata for originals in the `phi` S3 bucket. |

Retention: account lifetime, hard delete 30 days after account deletion, user data key crypto-shredded so
backups expire unreadable (see retention matrix). The PHI service owner is `security-engineer`.

## Pseudonymisation convention

Implemented by `.claude/skills/medilens-data-engineer/scripts/pseudonymize.py`.

- **Function:** `HMAC-SHA256(key, utf8(str(value)))`, hex digest. Empty or null values stay null. The same input and key give the same pseudonym, so joins across tables still work.
- **Key:** `MEDILENS_HMAC_KEY` from the environment (AWS Secrets Manager), at least 32 characters, never in the repo, logs or notebooks. The script exits 2 if it is missing or short.
- **Rotation:** the key is rotated on a schedule and on suspected exposure; rotation changes every pseudonym, so analytics tables are rebuilt or re-keyed and old keys are retired with the data they covered (analytics retention is 2 years rolling). Pseudonyms from different key generations must not be joined. The rotation period is a security-engineer decision (open item).
- **Which columns** (`export` in the CSV):
  - `hash`: ids that link a person or record (`profile_id`, `owner_user_id`, `user_id`, `grantee_user_id`, `external_sub`, `actor_id`, `resource_id`, and own ids/foreign keys of clinical tables).
  - `band`: `birth_year` becomes a 5-year band (`1985-1989`) via `--birth-year-band`.
  - `drop`: free text, dates, codes that identify a condition, `ip`, `user_agent`, all `phi.*` direct identifiers.
  - `keep`: C1/C2 technical columns and the few coded C4 columns the product analytics need (`region_code`, `unit_code`, `department_code`, `doc_type`, `sex_at_birth`, `is_minor`).
- **Consumers:** analytics/gold models (dbt), product and AI-quality dashboards, ML dataset builds, DSR deletion verification. Consumers receive the exported form only; none gets the key. Prompts to external providers go through the AI gateway redaction, not through this script.
- Pseudonymised data is still personal data under Law 91/2025/QH15; it is not treated as anonymous.

Example: `MEDILENS_HMAC_KEY=... python pseudonymize.py in.csv out.csv --hash profile_id actor_id --drop ip user_agent --birth-year-band birth_year`

## Keeping the catalog complete

`python3 tools/check_data_catalog.py [MIGRATIONS_DIR] [CATALOG_CSV]` reads the migrations and exits 1 if
any column they create (`_TABLES` entries, literal `CREATE TABLE`, `ADD COLUMN`) has no row in
`columns.csv`, or if a row has an invalid class, category or export, an empty retention/owner/source, or
is duplicated. When a migration adds a column, add its row in the same PR and get the data-engineer
review. Tests: `tools/test_check_data_catalog.py`.

Open items: the check is not yet wired into CI (CI files are outside this task); stale catalog rows
(column removed by a migration) are not flagged; outbox purge period (7 days) is a proposal.
