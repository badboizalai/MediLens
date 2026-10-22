# PHI Service, Identity Link and AI Gateway — backend view (plan section 24)

## Boundaries
| Component | May access | May NOT access |
| --- | --- | --- |
| API modules (identity, sharing, admin…) | identity schema, Identity Link (to resolve `subject_key`), PHI Service API | clinical schema or `phi` bucket directly |
| PHI Service | clinical schema (own DB role), `phi` bucket, KMS (DEK wrap/unwrap) | identity schema (names, emails, phones) |
| Worker | quarantine bucket (read), PHI Service API (write results), AI Gateway | LLM providers directly, internet |
| AI Gateway | provider endpoints via VPC endpoints | clinical DB, identity DB |

Maturity A (MVP): PHI Service is a module in the monolith with its own schema, DB role and RLS; AI Gateway is a shared library. Maturity B (before real data, G3-P): both run as separate ECS services with separate IAM task roles; IAM denies `bedrock:InvokeModel*` to all other roles.

## Identity Link
Table `identity_link(user_id, subject_key, created_at)` in the identity store; `subject_key` = random 128-bit id (not derived from user data). Clinical rows carry only `subject_key` + `profile_id` (SEC-AR-02). Re-identification happens only in the API layer for the owner or an authorised share.

## Per-record envelope encryption
- On create: PHI Service asks KMS `GenerateDataKey` under the PHI CMK → encrypts sensitive columns/files with the plaintext DEK → stores the wrapped DEK with the record → discards plaintext.
- On read: unwrap via KMS (cached in memory briefly, never logged) → decrypt.
- On delete: destroy the wrapped DEK (and its copies in backups expire per policy) → crypto-shredding (SEC-AR-06).
- Rotation: CMK yearly (KMS); DEKs re-wrapped lazily.

## Authorization
Cedar policies for owner access, caregiver profiles, shares (scope, expiry), admin break-glass; policy tests per rule (BR-006, BR-030, BR-031) in CI (SEC-AR-07). RLS stays as the second layer.

## Audit
Every PHI read/write emits an AuditEvent with hash chaining (`hash = sha256(prev_hash + event)`), stored append-only (Object Lock); daily integrity job (SEC-AR-05).

## Calling the AI Gateway
Use the internal client only; pass `subject_key`, never names; set `task`, `unit`, `prompt_version`, `schema_version`, `priority`; handle `budget_exceeded`, `quota_exceeded`, `schema_invalid`, `needs_review` as Problem Details; store `tier`, `model_id`, tokens and `usd` in `extraction_runs`.

## Tests to keep
Clinical schema contains no identity columns (schema test) · API role cannot `SELECT` clinical tables (SQL test) · worker task role cannot reach the internet (network test in staging) · deleted record unreadable after DEK destruction · break-glass emits alert · gateway rejects unknown model ids.
