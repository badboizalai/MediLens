# ADR-0006: System access to RLS-protected tables via SECURITY DEFINER functions

- **Status:** Accepted (2026-10-23, decided by main session on owner's "Tiếp tục" instruction; owner may override)
- **Date:** 2026-10-23
- **Deciders:** Solution Architect (reviewers: security-engineer, backend-engineer)
- **Related:** ADR-0002 (modular monolith), ADR-0005 (worker to API hand-off), RULES C2/C6, SEC authorization on every endpoint, BR-042; tasks S6-T53d, S6-T53d2

## Context
`clinical.*` tables use FORCE row level security keyed on `app.profile_ids` (the caller's profiles). The `api-events` consumer (ADR-0005) is a background process with no user and no profile scope, yet must update `clinical.documents.status` and later ingest extraction results. Without a rule, each such path would invent its own bypass, and any bypass over PHI tables is a high-impact security decision.

## Options considered
1. Widen `app.profile_ids` to all profiles for the consumer. Pros: no schema change. Cons: the consumer (and any bug or injection in it) can read and write every patient's rows; RLS becomes meaningless for that role.
2. `BYPASSRLS` on `app_rw` or on the consumer login. Pros: trivial. Cons: same blast radius, and on `app_rw` it disables RLS for the user-facing API too; rejected outright.
3. Per-event profile lookup by the consumer (read the owner, then set scope). Pros: scoped writes. Cons: the lookup itself needs cross-profile read access, so the problem moves; extra query per event.
4. Narrow `SECURITY DEFINER` SQL functions, one purpose each, callable only by the consumer role. Pros: the consumer can do exactly the listed operations and nothing else; reviewable in migrations. Cons: one function (and review) per system write path.

## Decision
Option 4. Background workers or consumers without profile scope reach RLS tables ONLY through functions created by Alembic migrations that:
- are owned by a dedicated `NOLOGIN` role that has the minimum table privileges needed;
- set `SET search_path = pg_catalog, pg_temp` and reference every object schema-qualified;
- have one purpose each, taking ids and enum values, never free SQL or text. Example: `clinical.apply_document_status(document_id, new_status)` updates only the status and transition fields of `clinical.documents` by id, with the state-machine guard (forward-only, idempotent, unknown id is a no-op);
- have `REVOKE EXECUTE ... FROM PUBLIC`, and `GRANT EXECUTE` only to the consumer role;
- are used by a consumer role that holds no table privileges of its own.

Tests for these paths run as the non-superuser consumer role (a superuser would bypass RLS and hide defects), and include a negative test that the role cannot `SELECT`/`UPDATE` the tables directly.

## Consequences
- Positive: least privilege; the system path cannot read PHI it was not designed to touch; RLS stays enforced for the API role; behaviour is auditable in migrations.
- Negative / trade-offs: every new system write path (for example S6-T53d2 extraction ingest) needs its own function, migration and security review; functions are reviewed like endpoints (authorization, input validation, test); `SECURITY DEFINER` mistakes (search_path, PUBLIC execute) are dangerous, so the checklist above is mandatory.
- Follow-up tasks: S6-T53d status applier uses `clinical.apply_document_status`; S6-T53d2 adds the extraction ingest function.

## Addendum (S6-T53d2)
`clinical.ingest_extraction()` (migration 0005) follows this pattern with its own NOLOGIN owner `extraction_ingest_definer`: SELECT of `documents(id, profile_id, deleted_at)`, INSERT-only column grants on `extraction_runs` and `extraction_fields`, `profile_id` derived from the document, idempotent on the run id, EXECUTE only for `api_events_consumer`. Nuance: `INSERT ... ON CONFLICT` evaluates SELECT policies, so the `extraction_runs` policy for the definer has no `FOR` clause; the column grants (SELECT `id` only) still cap what it can read.

## Exit strategy
If system paths multiply beyond a handful, move them to a separate internal service with its own database role, keeping the same function signatures as the contract. Cost: one module, no data migration.

## Revisit when
More than about five definer functions exist; a system path needs to read PHI rather than write status; the consumer is split into its own service; a security review finds a bypass.
