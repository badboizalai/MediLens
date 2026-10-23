# Worker / API contracts (ADR-0005)

JSON Schema (draft 2020-12, `additionalProperties: false`) for the messages between worker and API. Owner: backend-engineer; reviewers: solution-architect, data-engineer. Any breaking change = new `schemaVersion` and a new schema file; additive optional fields are not allowed on closed objects, so every change is a version bump.

| Schema | Carries | Producer to consumer |
| --- | --- | --- |
| `job-message.schema.json` | `jobs` queue: `{type, documentId, attempt?}`; `storageKey`, `mime` only on `document.validate` (BUG-05a) | API outbox relay / worker runner to worker |
| `document-status-changed.schema.json` | `api-events`: `document.status_changed` | worker to API |
| `extraction-completed.schema.json` | `api-events`: `extraction.completed` (ids only) | worker to API |
| `extraction-result.schema.json` | S3 object `extractions/{documentId}/{runId}.json` (PHI) | worker writes, API reads |

Rules: messages hold ids and enums only (no PHI, no free text). `reason` codes match `^[a-z0-9_:]+$`. The `result` field of the extraction result is validated against `ml/schemas/<unit>.v1.json` (not duplicated here). Examples in `examples/` are synthetic: `<schema>.valid*.json` must validate, `<schema>.invalid*.json` must be rejected.

## Status mapping (worker `DocStatus` to API `clinical.documents.status`)

The API stores the worker value verbatim; only the pre-pipeline and upload-time states are API-only. The consumer ignores any incoming event whose rank is at or below the stored rank (regressions and duplicates), except for terminals below.

| Rank | Worker `DocStatus` | API `documents.status` | Set by |
| --- | --- | --- | --- |
| 0 | (none) | `uploaded-pending` | API (presign) |
| 1 | `uploaded` | `uploaded` | API (upload confirmed) |
| 2 | `validated` | `validated` | worker |
| 3 | `preprocessed` | `preprocessed` | worker |
| 4 | `classified` | `classified` | worker |
| 5 | `ocr_done` | `ocr_done` | worker |
| 6 | `extracted` | `extracted` | worker |
| 7 | `needs_review` | `needs_review` | worker, after `extraction.completed` is ingested |
| 8 | `confirmed` | `confirmed` | API (user confirms review) |
| terminal | `needs_retake` | `needs_retake` | worker (reason: `blurry`, `too_dark`, `not_a_document`) |
| terminal | `failed` | `failed` | worker (non-retryable or DLQ) |
| terminal | (not emitted) | `rejected` | API only (upload sniff/size check fails, BR-010/BR-016) |

Terminal handling:
- `needs_retake`, `failed` and `rejected` are accepted from any non-terminal state and then final: later events for the document are ignored.
- The only way out of `needs_retake` is the user re-uploading (`needs_retake` to `uploaded`, ALLOWED in worker `state.py`). That is an API action, not an event on `api-events`.
- `confirmed` is final and API-owned; the worker never emits it.
- `rejected` is not in the worker enum, so the `status` enum in `document-status-changed` excludes it by design.

## Field ownership

| Field | Owner (writes) | Other side |
| --- | --- | --- |
| `documentId`, `storageKey`, `mime` | API (assigned at presign / upload) | worker reads, never changes |
| `status`, `reason` | worker (pipeline steps) except `uploaded-pending`, `uploaded`, `confirmed`, `rejected` (API) | API stores, forward-only |
| `runId` | worker (generated per extraction run) | API ingest is idempotent on `(documentId, runId)` |
| `unit`, `model`, `promptVersion`, `costUsd`, `confidence`, `flags`, `result` | worker | API copies into `clinical.extraction_runs` / `extraction_fields` after validating the result |
| `user_value`, `confirmed_at` (`extraction_fields`) | API (review) | not in any contract |

Open point: the worker `ExtractionRun` has no `runId` or `pipelineVersion` yet; S6-T53c adds them when it writes the object.
