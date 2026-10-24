# apps/worker — AI pipeline worker
Pulls jobs from Redis, reads from object storage, writes to PostgreSQL. Never serves user requests. Owner skills: `medilens-ai-ml-engineer`, `medilens-backend-engineer`.

## Runtime (S5-T42)
- `queue/`: `Queue` protocol; `InMemoryQueue` (local/tests), `SqsQueue` (boto3; set `AWS_ENDPOINT_URL` for LocalStack). Env: `WORKER_QUEUE_URL`, `WORKER_DLQ_URL`.
- `pipeline/state.py`: allowed-transition table + `guard_transition`. `pipeline/runner.py`: dedup (`document_id:step:attempt`), exponential backoff retries, DLQ on max attempts / unknown type / poison message. Logs carry IDs only, never PHI.
- `jobs/registry.py`: one stub handler per step. TODO: OCR/preprocess S5-T43, LLM extraction S5-T45.

## Persistent stores (BUG-04)
Local default is in-memory. Set `WORKER_DATABASE_URL` for Postgres status/idempotency (schema `worker`, api migration `0003`; `PgIdempotencyStore.claim` is an atomic `INSERT ... ON CONFLICT DO NOTHING`). Set `WORKER_PAGES_BUCKET` (processed bucket; optional `WORKER_RAW_BUCKET`) for the S3 page store. Keys carry opaque ids only. Page and result writes use SSE-KMS (`aws:kms`, never AES256) with the PHI CMK from `PHI_KMS_KEY_ID`; unset falls back to the bucket default key.
Idempotency is a lease (`claim`/`mark`/`release`, `LEASE_SECONDS`): a done key is never re-claimed; an unfinished one is re-claimable after the lease. `document.validate` (BUG-05b) reads the upload at the `storageKey` in the job message (`quarantine/{profile_id}/{document_id}`, raw bucket), checks size/type/MIME/PDF pages and active content, and copies it to `raw/{document_id}/0000` in the pages bucket, which `S3PageStore.raw_pages` reads. Reasons: `raw_key_missing`, `file_too_large`, `unsupported_type`, `mime_mismatch`, `pdf_active_content`, `too_many_pages`, `image_too_large`, `malware_detected`. With `WORKER_REQUIRE_MALWARE_SCAN=true` the GuardDuty tag `GuardDutyMalwareScanStatus` must be `NO_THREATS_FOUND`; a missing tag retries (scan pending). The PDF page count is a byte-level `/Type /Page` count (shortcut).

## Container image and pixel cap (S6-T58-F4b)
`Dockerfile` builds the worker with the `ocr` extra (CPU-only torch; ~2.9 GB image), runs as non-root uid 10001, `CMD python -m medilens_worker.main`. Build: `docker build -t medilens-worker apps/worker`. No CI build step yet (workflows are out of scope for this change).
Images are rejected before any decode when the header declares more than `MAX_IMAGE_PIXELS` (50 MP, `intake/pixels.py`; A4 at 600 dpi is ~35 MP): intake reason `image_too_large` (unreadable header: `unsupported_type`), preprocess retake `not_a_document`, OCR adapter `ValueError`. Only PNG/JPEG headers are parsed (HEIC is never decoded).

## Wiring and service auth (BUG-03)
- `main.build_extract_deps()` configures `extraction.deps` at startup from env: `EXTRACTION_RESULTS_BUCKET`, `AI_GATEWAY_URL`, `AI_GATEWAY_SERVICE_SECRET`, `WORKER_TENANT_ID`. Missing any of them fails fast unless `ENV=local` (local gets dev defaults and an in-memory result store).
- Each extraction run has a `run_id` and `pipeline_version`; `storage/results.py` writes it (extraction-result schema) to `extractions/{documentId}/{runId}.json` (S3, SSE-KMS). `finalize` emits `extraction.completed {event, schemaVersion, documentId, runId}` through the EventSink (idempotent: same run, same runId); the runner then moves the document to `needs_review`.
- `HttpGatewayClient` mints a fresh 60 s HMAC token per request (`caller=worker`, `aud=ai-gateway`, scope = its tenant/profile) and sends `Authorization: Bearer`. `extraction/service_token.py` is a byte-identical copy of the gateway's (a test enforces it).
- Gateway replay cache is per process. shortcut: fine for one task; move nonces to Redis/DynamoDB when the gateway runs more than one.
- Still stubs: `validate` and `classify` (need raw-file access and a page classifier, not tiny).

## Chaining and status events (S6-T53b, ADR-0005)
After a step succeeds the runner sends `{"type": <next job>, "documentId", "attempt": 1}` to the jobs queue, where next is the registry job whose `src` equals this step's `dst` (ids only; `storageKey`/`mime` are never copied). A duplicate delivery whose document is already at `dst` re-sends the next step and the event (the next step's dedup key makes that safe). After every status write (including `needs_retake`/`failed` with reason codes) the runner sends `document.status_changed` to an `EventSink`: `SqsEventSink` when `API_EVENTS_QUEUE_URL` is set, otherwise an in-memory sink. Both message shapes are tested against `docs/architecture/contracts`. A `RetryLater` exception (e.g. `ScanPending`) carries its own budget (30 s x 20 attempts) instead of the normal 3 attempts.

## Region mapping (S7-T66b)
Extraction adds `region: {region_code, confidence}` to each located item (dental `teeth[]`, cardiology `diagnoses[]`, oncology `primary`/`metastases[]`) via `anatomy.map_region`. Unmapped items keep `region_code: null` and get a `region_unmapped` flag; none are dropped. Illustration only (BR-042). `runId` is uuid7; `latest()` picks the greatest runId.
