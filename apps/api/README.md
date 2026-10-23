# apps/api — FastAPI modular monolith
Hexagonal modules under `src/medilens/modules/<name>/{api,application,domain,infra}`. Rules: `api → application → domain`; `infra` implements domain interfaces; modules never query each other's tables (enforced by `import-linter`, run `make api-lint`). Owner skill: `medilens-backend-engineer`.

## Outbox relay
`DocumentService.complete` writes `DocumentUploaded` to `clinical.outbox`; the relay publishes it to the worker queue (at-least-once, the worker dedups). Run: `DATABASE_URL=... WORKER_QUEUE_URL=... [AWS_ENDPOINT_URL=...] python -m medilens.shared.outbox_relay` (polls every `POLL_INTERVAL_SECONDS`).
Message: `{"type":"document.validate","documentId":"<uuid>","storageKey":"quarantine/<profile_id>/<document_id>","mime":"<mime>","attempt":1}`. Unknown event types stay unpublished (logged by type only).
