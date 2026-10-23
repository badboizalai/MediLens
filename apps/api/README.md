# apps/api — FastAPI modular monolith
Hexagonal modules under `src/medilens/modules/<name>/{api,application,domain,infra}`. Rules: `api → application → domain`; `infra` implements domain interfaces; modules never query each other's tables (enforced by `import-linter`, run `make api-lint`). Owner skill: `medilens-backend-engineer`.

## Extraction review (S7-T63)
- `GET /v1/documents/{id}/fields` - latest run fields; `needs_confirmation` = confidence < 0.7 (BR-012)
- `PATCH /v1/documents/{id}/fields/{field_id}` `{user_value}` - edit and confirm one field
- `POST /v1/documents/{id}/confirm` - 409 listing unconfirmed low-confidence field ids, else 204 + audit event

Other users' documents/fields return 404 (RLS + owner scope). Audit rows carry actor/action/ids only.

## Document status stream (D53)
`GET /v1/documents/{id}/events` - Server-Sent Events (`text/event-stream`, `Cache-Control: no-cache`). Owner-only (404 otherwise, like `GET /documents/{id}`). Polls the status every 1 s; emits `event: status` / `data: {"status","updatedAt"}` immediately and on each change (`updatedAt` = when the API observed it), `: keep-alive` comments every 15 s. Closes on a terminal status (`rejected`, `needs_retake`, `failed`, `needs_review`, `confirmed`) or after 300 s; clients reconnect and get the current status first. Constants: `document/application/status_stream.py`. The stream is async (awaited sleep; only the DB poll uses a worker thread). Note: browser `EventSource` cannot send an `Authorization` header, so the web client must use fetch-streaming (e.g. `fetch` + `ReadableStream`) or cookie auth.

## Outbox relay
`DocumentService.complete` writes `DocumentUploaded` to `clinical.outbox`; the relay publishes it to the worker queue (at-least-once, the worker dedups). Run: `DATABASE_URL=... WORKER_QUEUE_URL=... [AWS_ENDPOINT_URL=...] python -m medilens.shared.outbox_relay` (polls every `POLL_INTERVAL_SECONDS`).
Message: `{"type":"document.validate","documentId":"<uuid>","storageKey":"quarantine/<profile_id>/<document_id>","mime":"<mime>","attempt":1}`. Unknown event types stay unpublished (logged by type only).

## api-events consumer
`python -m medilens.shared.api_events_consumer` (env `DATABASE_URL`, `API_EVENTS_QUEUE_URL`, optional `AWS_ENDPOINT_URL`) applies worker `document.status_changed` via `clinical.apply_document_status()` (migration 0004, SECURITY DEFINER, forward-only). Its DB login must be a member of the NOLOGIN role `api_events_consumer` (EXECUTE on that function only, no table access): `GRANT api_events_consumer TO <consumer_login>`. The function runs as `doc_status_definer`, let through FORCE RLS by one policy for that role alone.
It also ingests `extraction.completed` (S6-T53d2): env `RESULTS_BUCKET` names the PHI bucket; the consumer validates the message and the S3 result object (`extractions/{documentId}/{runId}.json`) against the contracts, then calls `clinical.ingest_extraction()` (migration 0005, owner `extraction_ingest_definer`, INSERT-only column grants, EXECUTE for `api_events_consumer` only). `profile_id` comes from the document row, never the message; the run id is the idempotency key (re-delivery inserts nothing); an unknown document is a permanent error (left for the DLQ).

## Clinical projection (S8-CLIN)
- `POST /v1/documents/{id}/confirm` also projects the confirmed run into `clinical.encounters / conditions / body_findings / observations` in the same transaction (wired in `main.py` via the extraction `get_confirm_hook`; modules never import each other). User edits (`user_value`) win over model values. No `region_code` -> a condition without a body finding. `is_metastasis` only for oncology `metastases[]` not stated as `suspected`. `icd10_code` is never written (LIC-002). Idempotent: rows carry `source_run_id` (migration 0006); re-confirming soft-deletes and re-creates that run's rows.
- `GET /v1/profiles/{profile_id}/findings?limit=&cursor=` - `{findings[], observations[], next_cursor}`; owner-only (404 otherwise, 401 unauthenticated). The cursor pages findings (newest first, max 100); observations are returned on the first page only.

## Knowledge RAG (S10-T95)
- `POST /v1/profiles/{profile_id}/knowledge/search` `{query, k<=10}` -> `{chunks[{content, article_id, language, title, citations[{title,url}], scope: article|profile, distance}]}`. Owner-only (404 otherwise, 401 unauthenticated). Returns public article chunks plus chunks of the caller's own profile; the `profile_id` filter is in the query AND in RLS on `clinical.knowledge_chunks` (migration 0007, needs the pgvector extension: dev/test use `pgvector/pgvector:pg16`). A cross-user query returns 0 profile chunks.
- Ingest articles (as migrator/superuser; app_rw cannot write public rows): `DATABASE_URL=... python -m medilens.modules.knowledge.ingest content/articles`. Chunks <= 800 chars by language section/paragraph, with article id, language and source citations.
- Only articles with a `cso_review_date` are retrievable unless `KNOWLEDGE_ALLOW_DRAFTS=true` (BR-024/BR-051; default false).
- Embeddings sit behind the `Embedder` port; `HashingEmbedder` (256-d, lexical) is a dev stand-in to replace with Bedrock Titan/Cohere via ai-gateway. `KnowledgeService.index_profile_text(profile_id, text, source_ref)` indexes per-profile text (trusted internal callers; no ownership check).
