# apps/worker — AI pipeline worker
Pulls jobs from Redis, reads from object storage, writes to PostgreSQL. Never serves user requests. Owner skills: `medilens-ai-ml-engineer`, `medilens-backend-engineer`.

## Runtime (S5-T42)
- `queue/`: `Queue` protocol; `InMemoryQueue` (local/tests), `SqsQueue` (boto3; set `AWS_ENDPOINT_URL` for LocalStack). Env: `WORKER_QUEUE_URL`, `WORKER_DLQ_URL`.
- `pipeline/state.py`: allowed-transition table + `guard_transition`. `pipeline/runner.py`: dedup (`document_id:step:attempt`), exponential backoff retries, DLQ on max attempts / unknown type / poison message. Logs carry IDs only, never PHI.
- `jobs/registry.py`: one stub handler per step. TODO: OCR/preprocess S5-T43, LLM extraction S5-T45.

## Persistent stores (BUG-04)
Local default is in-memory. Set `WORKER_DATABASE_URL` for Postgres status/idempotency (schema `worker`, api migration `0002`; `PgIdempotencyStore.claim` is an atomic `INSERT ... ON CONFLICT DO NOTHING`). Set `WORKER_PAGES_BUCKET` (processed bucket; optional `WORKER_RAW_BUCKET`) for the S3 page store. Keys carry opaque ids only.
Idempotency is a lease (`claim`/`mark`/`release`, `LEASE_SECONDS`): a done key is never re-claimed; an unfinished one is re-claimable after the lease. Raw pages are read from the API upload key (`quarantine/{profile_id}/{document_id}`) registered via `S3PageStore.register_raw`; the post-scan clean location is TBD.
