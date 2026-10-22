# Entity-relationship diagram

Source: plan section 8.2. Implemented by `apps/api/migrations/versions/0001_initial_schema.py`.

Conventions: UUIDv7 primary keys (`public.uuid_v7()`), `created_at`/`updated_at`/`deleted_at` on every
table (omitted below for brevity), no name/email/phone columns in the `clinical` schema (identifiers
live in `identity` / the PHI service). Row-Level Security on clinical tables by `profile_id` via
`current_setting('app.profile_ids')`. Roles: `migrator` (DDL), `app_rw` (DML), `app_ro` (read-only).

```mermaid
erDiagram
  USERS ||--o{ PATIENT_PROFILES : owns
  USERS ||--o{ CONSENTS : gives
  USERS ||--o{ SHARE_GRANTS : "is grantee"
  PATIENT_PROFILES ||--o{ DOCUMENTS : has
  PATIENT_PROFILES ||--o{ ENCOUNTERS : has
  PATIENT_PROFILES ||--o{ CONDITIONS : has
  PATIENT_PROFILES ||--o{ OBSERVATIONS : has
  PATIENT_PROFILES ||--o{ SHARE_GRANTS : shares
  DOCUMENTS ||--o{ DOCUMENT_PAGES : contains
  DOCUMENTS ||--o{ EXTRACTION_RUNS : "processed by"
  EXTRACTION_RUNS ||--o{ EXTRACTION_FIELDS : yields
  ENCOUNTERS ||--o{ CONDITIONS : records
  CONDITIONS ||--o{ BODY_FINDINGS : "drawn as"
  UNITS ||--o{ UNIT_CONFIGS : versions
  REGIONS ||..o{ BODY_FINDINGS : "region_code"

  USERS { uuid id PK; text external_sub; text status }
  PATIENT_PROFILES { uuid id PK; uuid owner_user_id FK; int birth_year; text sex_at_birth; bool is_minor }
  CONSENTS { uuid id PK; uuid user_id FK; text type; text terms_version; timestamptz given_at; timestamptz withdrawn_at }
  DOCUMENTS { uuid id PK; uuid profile_id FK; text storage_key; text sha256; text mime; int pages; text status; text doc_type }
  DOCUMENT_PAGES { uuid id PK; uuid profile_id; uuid document_id FK; int page_no; text ocr_text; jsonb ocr_boxes; real quality_score }
  EXTRACTION_RUNS { uuid id PK; uuid profile_id; uuid document_id FK; text pipeline_version; text model; text prompt_version; jsonb raw_output; real confidence; numeric cost_usd; text status }
  EXTRACTION_FIELDS { uuid id PK; uuid profile_id; uuid run_id FK; text field_path; text value; real confidence; int source_page; jsonb source_box; text user_value; timestamptz confirmed_at }
  ENCOUNTERS { uuid id PK; uuid profile_id FK; date date; text facility; text department_code }
  CONDITIONS { uuid id PK; uuid profile_id FK; uuid encounter_id FK; text icd10_code; text unit_code; text status; text severity; text stage; date onset_date }
  BODY_FINDINGS { uuid id PK; uuid profile_id; uuid condition_id FK; text region_code; text laterality; numeric size_mm; text severity; bool is_metastasis; timestamptz observed_at }
  OBSERVATIONS { uuid id PK; uuid profile_id FK; text loinc_code; text name; text value; text unit; numeric ref_low; numeric ref_high; timestamptz observed_at }
  SHARE_GRANTS { uuid id PK; uuid profile_id FK; uuid grantee_user_id FK; text scope; timestamptz expires_at; timestamptz revoked_at }
  UNITS { uuid id PK; text code; text name_vi; text name_en; text parent_code; text mesh_id; text svg_id; text std_code }
  REGIONS { uuid id PK; text code; text name_vi; text name_en; text parent_code; text mesh_id; text svg_id; text std_code }
  UNIT_CONFIGS { uuid id PK; text unit_code FK; int version; jsonb config; timestamptz published_at }
  AUDIT_EVENTS { uuid id PK; timestamptz at PK; uuid actor_id; text action; text resource_type; uuid resource_id; inet ip; text user_agent }
  OUTBOX { uuid id PK; text event_type; jsonb payload; timestamptz published_at }
```

## Schemas

| Schema | Tables | RLS |
| --- | --- | --- |
| `identity` | users, patient_profiles, consents | no (access via application services) |
| `clinical` | documents, document_pages, extraction_runs, extraction_fields, encounters, conditions, body_findings, observations, share_grants, units, regions, unit_configs, outbox | yes on all profile-scoped tables (catalogues and outbox excluded) |
| `audit` | audit_events (monthly range partitions + default; `audit.ensure_partition(date)`) | append-only: `app_rw` has INSERT/SELECT only |

Child tables (`document_pages`, `extraction_runs`, `extraction_fields`, `body_findings`) carry a
denormalised `profile_id` so a single policy applies; the API must set it from the parent row.
`knowledge_articles/chunks` (vector) are deferred to the knowledge-module migration.
