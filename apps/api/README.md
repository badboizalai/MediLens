# apps/api — FastAPI modular monolith
Hexagonal modules under `src/medilens/modules/<name>/{api,application,domain,infra}`. Rules: `api → application → domain`; `infra` implements domain interfaces; modules never query each other's tables (enforced by `import-linter`, run `make api-lint`). Owner skill: `medilens-backend-engineer`.

## Extraction review (S7-T63)
- `GET /v1/documents/{id}/fields` - latest run fields; `needs_confirmation` = confidence < 0.7 (BR-012)
- `PATCH /v1/documents/{id}/fields/{field_id}` `{user_value}` - edit and confirm one field
- `POST /v1/documents/{id}/confirm` - 409 listing unconfirmed low-confidence field ids, else 204 + audit event

Other users' documents/fields return 404 (RLS + owner scope). Audit rows carry actor/action/ids only.

## Document status stream (D53)
`GET /v1/documents/{id}/events` - Server-Sent Events (`text/event-stream`, `Cache-Control: no-cache`). Owner-only (404 otherwise, like `GET /documents/{id}`). Polls the status every 1 s; emits `event: status` / `data: {"status","updatedAt"}` immediately and on each change (`updatedAt` = when the API observed it), `: keep-alive` comments every 15 s. Closes on a terminal status (`rejected`, `needs_retake`, `failed`, `needs_review`, `confirmed`) or after 300 s; clients reconnect and get the current status first. Constants: `document/application/status_stream.py`. The stream is async (awaited sleep; only the DB poll uses a worker thread). Note: browser `EventSource` cannot send an `Authorization` header, so the web client must use fetch-streaming (e.g. `fetch` + `ReadableStream`) or cookie auth.

## Admin without PHI + break-glass (S11-T105, SEC-AZ-05)
Admin = token role/group `MEDILENS_ADMIN_ROLE` (default `medilens-admin`); others get 403, no token 401.
- `GET /v1/admin/stats` - counts only (documents per status, users) via `audit.admin_stats()` (migration 0006, SECURITY DEFINER, owner `admin_definer`); no clinical row is ever readable by an admin.
- `POST /v1/admin/break-glass` `{profile_id, reason (>=10 chars), ticket?}` - 201 grant valid 1 h (`BREAK_GLASS_TTL`), bound to the admin's `sub`; writes audit `break_glass.opened` and fires the `AlertSink` (default: structured WARNING `break_glass.opened`, ids only, never the reason; a failing sink rolls the grant back).
- `GET /v1/admin/break-glass/{grant_id}/documents` - `[{id, status}]` of that one profile via `audit.break_glass_documents()`, which re-checks owner/expiry/revocation with `now()`; expired, revoked, foreign or unknown grant -> 403. Each read audits `break_glass.read_documents`.

No BYPASSRLS and `app.profile_ids` is never widened (ADR-0006 definer pattern). Grants are insert-only for `app_rw`; revocation is an operator action (`revoked_at`), no endpoint yet.

## Outbox relay
`DocumentService.complete` writes `DocumentUploaded` to `clinical.outbox`; the relay publishes it to the worker queue (at-least-once, the worker dedups). Run: `DATABASE_URL=... WORKER_QUEUE_URL=... [AWS_ENDPOINT_URL=...] python -m medilens.shared.outbox_relay` (polls every `POLL_INTERVAL_SECONDS`).
Message: `{"type":"document.validate","documentId":"<uuid>","storageKey":"quarantine/<profile_id>/<document_id>","mime":"<mime>","attempt":1}`. Unknown event types stay unpublished (logged by type only).

## api-events consumer
`python -m medilens.shared.api_events_consumer` (env `DATABASE_URL`, `API_EVENTS_QUEUE_URL`, optional `AWS_ENDPOINT_URL`) applies worker `document.status_changed` via `clinical.apply_document_status()` (migration 0004, SECURITY DEFINER, forward-only). Its DB login must be a member of the NOLOGIN role `api_events_consumer` (EXECUTE on that function only, no table access): `GRANT api_events_consumer TO <consumer_login>`. The function runs as `doc_status_definer`, let through FORCE RLS by one policy for that role alone.
It also ingests `extraction.completed` (S6-T53d2): env `RESULTS_BUCKET` names the PHI bucket; the consumer validates the message and the S3 result object (`extractions/{documentId}/{runId}.json`) against the contracts, then calls `clinical.ingest_extraction()` (migration 0005, owner `extraction_ingest_definer`, INSERT-only column grants, EXECUTE for `api_events_consumer` only). `profile_id` comes from the document row, never the message; the run id is the idempotency key (re-delivery inserts nothing); an unknown document is a permanent error (left for the DLQ).

## Clinical projection (S8-CLIN)
- `POST /v1/documents/{id}/confirm` also projects the confirmed run into `clinical.encounters / conditions / body_findings / observations` in the same transaction (wired in `main.py` via the extraction `get_confirm_hook`; modules never import each other). User edits (`user_value`) win over model values. No `region_code` -> a condition without a body finding. `is_metastasis` only for oncology `metastases[]` not stated as `suspected`. `icd10_code` is never written (LIC-002). Idempotent: rows carry `source_run_id` (migration 0006); re-confirming soft-deletes and re-creates that run's rows.
- `GET /v1/profiles/{profile_id}/findings?limit=&cursor=` - `{findings[], observations[], next_cursor}`; owner-only (404 otherwise, 401 unauthenticated). The cursor pages findings (newest first, max 100); observations are returned on the first page only.

## Patient-reported findings (S11-T102, BR-040/041)
- `POST /v1/profiles/{profile_id}/reported-findings` `{text (<=500, not blank), observed_at?}`, owner-only (401/404).
- Emergency signs (copy of the ai-gateway keyword list, `domain/models.py`) -> `200 {emergency: true, message_key: "emergency_115"}` and **nothing is stored**; the web shows 115 before any other content.
- Otherwise `201 {emergency: false, label_key: "you_described", condition_id, region_code?, laterality?}`. A dictionary NER (`infra/location_ner.py`, reads `data/terminology/location-synonyms.v1.yaml`, dir via `MEDILENS_TERMINOLOGY_DIR`) maps the text to a `region_code`; side words trai/phai/left/right; several regions, group nodes or an unknown side on a paired organ -> unmapped (condition kept, no body finding, never guessed).
- Stored as `clinical.conditions.source = 'patient_reported'` (migration 0007), `icd10_code` and `severity` NULL. `GET .../findings` returns `source` (`record` | `patient_reported`) so the web labels "you described". Text is never logged.
