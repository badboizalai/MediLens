# ADR-0005: Worker to API hand-off of document status and extraction results

- **Status:** Proposed
- **Date:** 2026-10-23
- **Deciders:** Solution Architect (reviewers: backend-engineer, security-engineer)
- **Related:** ADR-0002 (modular monolith), ADR-010 (outbox, plan §16.3), NFR-01, NFR-04, NFR-08, NFR-15, BR-042; task S6-T53 / D53

## Context
Facts on `main` (verified in code):
- The worker owns schema `worker` (`worker.document_status`, `worker.idempotency_keys`, migration 0003) and must not touch API tables.
- The API owns `clinical.documents.status`, `clinical.extraction_runs`, `clinical.extraction_fields` and `clinical.outbox`. The outbox relay (API to worker jobs on SQS) is in progress (BUG-05a).
- `pipeline/runner.py` sets the worker status after each step but never tells the API and never enqueues the next step. Extraction runs and reviews live in memory (`extraction/deps.py`, `main.py` `build_extract_deps`), so the review API has nothing to read.
- Extracted values are PHI: they must not appear in queue messages or logs (messages carry ids only).
- D53 needs status changes visible to the client in under 2 s (SSE). Scale is MVP (NFR-15: 100 MAU, one operator), so the smallest mechanism that keeps module ownership wins.

Four decisions are needed: (1) step chaining, (2) status back-channel, (3) extraction result transfer, (4) SSE source.

## Options considered
**(1) Step chaining**
1. Runner enqueues the next step itself after a successful step. Pros: about 10 lines, uses the existing `REGISTRY` (`src`/`dst`), no new component. Cons: chain logic is implicit in the registry.
2. Orchestrator (Step Functions or a saga table). Pros: explicit flow, visual retries. Cons: new infra and cost, overkill for a linear 6-step chain.

**(2) Status back-channel**
1. Worker sends `document.status_changed` to a dedicated SQS `api-events` queue (plus DLQ); an API consumer applies it to `clinical.documents.status`. Pros: mirrors the outbox pattern already in use, keeps schema ownership, at-least-once, decoupled from API availability. Cons: one more queue and consumer loop.
2. API reads `worker.document_status` through a view or direct query. Pros: no queue. Cons: breaks the "worker schema is private, modules talk via services/events" rule (ADR-0002); couples releases; API would need grants on the worker schema.
3. EventBridge bus. Pros: fan-out. Cons: no second consumer exists; extra service and cost.

**(3) Extraction result transfer (PHI)**
1. Worker writes the result JSON to the PHI bucket (SSE-KMS) at `extractions/{documentId}/{runId}.json` and emits `extraction.completed {documentId, runId}` (ids only, on `api-events`). The API consumer reads the object and inserts `extraction_runs`/`extraction_fields` in one transaction, then sets status to the review state. Pros: PHI never in queue or logs; replayable; no new endpoint; reuses the page store pattern. Cons: extra S3 read and a JSON schema to version.
2. Worker POSTs results to an internal API endpoint with the service token. Pros: simple and synchronous. Cons: worker availability depends on API, needs its own retry/idempotency, large bodies through the API, a new endpoint to authorize and test.
3. Worker writes directly to `clinical.*`. Cons: violates ownership; rejected.

**(4) SSE source**
1. Each open stream polls the API's own `clinical.documents` (by id and `updated_at`) every 1 s. Pros: stateless, works across ECS tasks, trivial. Cons: one cheap indexed query per open stream per second.
2. Postgres LISTEN/NOTIFY fired by the consumer. Pros: lower latency and load. Cons: holds a connection per task, needs reconnect handling; premature at MVP scale.

## Decision
- (1) Option 1: after a step succeeds the runner enqueues the message for the registry job whose `src` equals the step's `dst`. Messages are `{type, documentId, attempt}` only. If the document is already at `dst` (duplicate delivery) the runner re-enqueues the next step, since the next step's own dedup key makes this safe, so a crash between `set` and `send` cannot stall the chain.
- (2) Option 1: the worker sends `{event: "document.status_changed", documentId, status, reason?}` to the `api-events` SQS queue after every status write (including terminal and failed). The API consumer applies transitions forward-only and idempotently (ignore if the stored status is already at or past the incoming one) and drops unknown ids. Reason codes are enums, never text.
- (3) Option 1: result JSON goes to the PHI bucket under a key derived from ids; the event carries ids only. The API validates the document owner and the object against a JSON Schema before ingest; ingest is idempotent on `(documentId, runId)`. Worker IAM gets `s3:PutObject` on `extractions/*`; API gets `s3:GetObject` on the same prefix; both use the existing KMS key.
- (4) Option 1: SSE polls `clinical.documents` every 1 s per open stream. Budget: worker send plus consumer long-poll receive (about 0.5 s) plus up to 1 s poll is under 2 s p95; confirm with a load test before accepting.

Why: it is the smallest set (one queue, one S3 prefix, one consumer) that keeps schema ownership, keeps PHI out of messages and logs, and needs no new managed service.

## Consequences
- Positive: no cross-schema access; at-least-once with idempotent consumers; failures are visible as DLQ depth; the review API gets real rows; no new AWS service beyond one SQS queue pair.
- Negative / trade-offs: eventual consistency (status in API lags the worker by about a second); two message contracts (`jobs`, `api-events`) to version; 1 s polling load grows linearly with open streams (fine at MVP); a poison `api-events` message needs a DLQ alarm.
- Follow-up tasks (each small, one PR):
  - S6-T53a Terraform: `api-events` queue + DLQ, alarms, S3 `extractions/*` IAM for worker (put) and API (get). Paths: `infra/terraform/envs/staging/`, `infra/terraform/modules/`.
  - S6-T53b Worker chaining + event emit: runner enqueues next step and sends status events; `Queue` port gains the events queue. Tests with the in-memory queue. Paths: `apps/worker/src/medilens_worker/pipeline/`, `apps/worker/src/medilens_worker/queue/`, `apps/worker/tests/`.
  - S6-T53c Worker result export: write result JSON to S3 and emit `extraction.completed`, replacing in-memory `save_run`/`save_review`. Paths: `apps/worker/src/medilens_worker/extraction/`, `apps/worker/src/medilens_worker/main.py`, `apps/worker/tests/`.
  - S6-T53d API consumer: status applier and extraction ingest into `extraction_runs`/`fields`, with an authz/ownership test. Paths: `apps/api/src/medilens/modules/document/`, `apps/api/src/medilens/modules/extraction/`, `apps/api/tests/`.
  - S6-T53e Status API + SSE (D53) polling the documents table, with a latency test. Paths: `apps/api/src/medilens/modules/document/api/`, `apps/api/tests/`, `tests/`.
  - Contract: JSON Schemas for both events and the result object in `docs/architecture/` (owner: backend-engineer).

## Exit strategy
Replace the polling loop with LISTEN/NOTIFY (4.2) without changing the contract. If a second consumer of status events appears, put EventBridge in front of `api-events`. If a step flow gets branches, move chaining to Step Functions; the registry `src`/`dst` pairs map directly to states. Cost of each: one module, no data migration.

## Revisit when
SSE p95 exceeds 2 s in the load test; open streams exceed about 500 concurrent; the pipeline gains parallel or branching steps; `api-events` DLQ is non-empty more than once a month; another service needs worker status.
