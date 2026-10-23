# apps/worker — AI pipeline worker
Pulls jobs from Redis, reads from object storage, writes to PostgreSQL. Never serves user requests. Owner skills: `medilens-ai-ml-engineer`, `medilens-backend-engineer`.

## Runtime (S5-T42)
- `queue/`: `Queue` protocol; `InMemoryQueue` (local/tests), `SqsQueue` (boto3; set `AWS_ENDPOINT_URL` for LocalStack). Env: `WORKER_QUEUE_URL`, `WORKER_DLQ_URL`.
- `pipeline/state.py`: allowed-transition table + `guard_transition`. `pipeline/runner.py`: dedup (`document_id:step:attempt`), exponential backoff retries, DLQ on max attempts / unknown type / poison message. Logs carry IDs only, never PHI.
- `jobs/registry.py`: one stub handler per step. TODO: OCR/preprocess S5-T43, LLM extraction S5-T45.

## Persistent stores (BUG-04)
Local default is in-memory. Set `WORKER_DATABASE_URL` for Postgres status/idempotency (schema `worker`, api migration `0003`; `PgIdempotencyStore.claim` is an atomic `INSERT ... ON CONFLICT DO NOTHING`). Set `WORKER_PAGES_BUCKET` (processed bucket; optional `WORKER_RAW_BUCKET`) for the S3 page store. Keys carry opaque ids only.
Idempotency is a lease (`claim`/`mark`/`release`, `LEASE_SECONDS`): a done key is never re-claimed; an unfinished one is re-claimable after the lease. `document.validate` (BUG-05b) reads the upload at the `storageKey` in the job message (`quarantine/{profile_id}/{document_id}`, raw bucket), checks size/type/MIME/PDF pages and active content, and copies it to `raw/{document_id}/0000` in the pages bucket, which `S3PageStore.raw_pages` reads. Reasons: `raw_key_missing`, `file_too_large`, `unsupported_type`, `mime_mismatch`, `pdf_active_content`, `too_many_pages`, `malware_detected`. With `WORKER_REQUIRE_MALWARE_SCAN=true` the GuardDuty tag `GuardDutyMalwareScanStatus` must be `NO_THREATS_FOUND`; a missing tag retries (scan pending). The PDF page count is a byte-level `/Type /Page` count (shortcut).

## Wiring and service auth (BUG-03)
- `main.build_extract_deps()` configures `extraction.deps` at startup from env: `AI_GATEWAY_URL`, `AI_GATEWAY_SERVICE_SECRET`, `WORKER_TENANT_ID`. Missing any of them fails fast unless `ENV=local` (local gets dev defaults). Runs/reviews are in memory until the DB store (BUG-04) replaces them.
- `finalize` loads the saved run via `ExtractDeps.load_run` and hands it to `save_review`; the runner then moves the document to `needs_review`.
- `HttpGatewayClient` mints a fresh 60 s HMAC token per request (`caller=worker`, `aud=ai-gateway`, scope = its tenant/profile) and sends `Authorization: Bearer`. `extraction/service_token.py` is a byte-identical copy of the gateway's (a test enforces it).
- Gateway replay cache is per process. shortcut: fine for one task; move nonces to Redis/DynamoDB when the gateway runs more than one.
- Still stubs: `validate` and `classify` (need raw-file access and a page classifier, not tiny).
