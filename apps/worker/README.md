# apps/worker — AI pipeline worker
Pulls jobs from Redis, reads from object storage, writes to PostgreSQL. Never serves user requests. Owner skills: `medilens-ai-ml-engineer`, `medilens-backend-engineer`.

## Runtime (S5-T42)
- `queue/`: `Queue` protocol; `InMemoryQueue` (local/tests), `SqsQueue` (boto3; set `AWS_ENDPOINT_URL` for LocalStack). Env: `WORKER_QUEUE_URL`, `WORKER_DLQ_URL`.
- `pipeline/state.py`: allowed-transition table + `guard_transition`. `pipeline/runner.py`: dedup (`document_id:step:attempt`), exponential backoff retries, DLQ on max attempts / unknown type / poison message. Logs carry IDs only, never PHI.
- `jobs/registry.py`: one stub handler per step. TODO: OCR/preprocess S5-T43, LLM extraction S5-T45.

## Wiring and service auth (BUG-03)
- `main.build_extract_deps()` configures `extraction.deps` at startup from env: `AI_GATEWAY_URL`, `AI_GATEWAY_SERVICE_SECRET`, `WORKER_TENANT_ID`. Missing any of them fails fast unless `ENV=local` (local gets dev defaults). Runs/reviews are in memory until the DB store (BUG-04) replaces them.
- `finalize` loads the saved run via `ExtractDeps.load_run` and hands it to `save_review`; the runner then moves the document to `needs_review`.
- `HttpGatewayClient` mints a fresh 60 s HMAC token per request (`caller=worker`, `aud=ai-gateway`, scope = its tenant/profile) and sends `Authorization: Bearer`. `extraction/service_token.py` is a byte-identical copy of the gateway's (a test enforces it).
- Gateway replay cache is per process. shortcut: fine for one task; move nonces to Redis/DynamoDB when the gateway runs more than one.
- Still stubs: `validate` and `classify` (need raw-file access and a page classifier, not tiny).
