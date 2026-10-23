# apps/api — FastAPI modular monolith
Hexagonal modules under `src/medilens/modules/<name>/{api,application,domain,infra}`. Rules: `api → application → domain`; `infra` implements domain interfaces; modules never query each other's tables (enforced by `import-linter`, run `make api-lint`). Owner skill: `medilens-backend-engineer`.

## Extraction review (S7-T63)
- `GET /v1/documents/{id}/fields` - latest run fields; `needs_confirmation` = confidence < 0.7 (BR-012)
- `PATCH /v1/documents/{id}/fields/{field_id}` `{user_value}` - edit and confirm one field
- `POST /v1/documents/{id}/confirm` - 409 listing unconfirmed low-confidence field ids, else 204 + audit event

Other users' documents/fields return 404 (RLS + owner scope). Audit rows carry actor/action/ids only.

## Outbox relay
`DocumentService.complete` writes `DocumentUploaded` to `clinical.outbox`; the relay publishes it to the worker queue (at-least-once, the worker dedups). Run: `DATABASE_URL=... WORKER_QUEUE_URL=... [AWS_ENDPOINT_URL=...] python -m medilens.shared.outbox_relay` (polls every `POLL_INTERVAL_SECONDS`).
Message: `{"type":"document.validate","documentId":"<uuid>","storageKey":"quarantine/<profile_id>/<document_id>","mime":"<mime>","attempt":1}`. Unknown event types stay unpublished (logged by type only).

## api-events consumer
`python -m medilens.shared.api_events_consumer` (env `DATABASE_URL`, `API_EVENTS_QUEUE_URL`, optional `AWS_ENDPOINT_URL`) applies worker `document.status_changed` via `clinical.apply_document_status()` (migration 0004, SECURITY DEFINER, forward-only). Its DB login must be a member of the NOLOGIN role `api_events_consumer` (EXECUTE on that function only, no table access): `GRANT api_events_consumer TO <consumer_login>`. The function runs as `doc_status_definer`, let through FORCE RLS by one policy for that role alone.
It also ingests `extraction.completed` (S6-T53d2): env `RESULTS_BUCKET` names the PHI bucket; the consumer validates the message and the S3 result object (`extractions/{documentId}/{runId}.json`) against the contracts, then calls `clinical.ingest_extraction()` (migration 0005, owner `extraction_ingest_definer`, INSERT-only column grants, EXECUTE for `api_events_consumer` only). `profile_id` comes from the document row, never the message; the run id is the idempotency key (re-delivery inserts nothing); an unknown document is a permanent error (left for the DLQ).
