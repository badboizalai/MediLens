# Design Note — <feature>

## Problem and goals
## Constraints (NFR, SEC, BR)
## Components touched
## Sequence
```mermaid
sequenceDiagram
  participant U as User (browser)
  participant API as API
  participant S3 as S3
  participant Q as SQS
  participant W as Worker
  U->>API: POST /medical-documents (presign)
  API-->>U: presigned URL
  U->>S3: PUT file
  U->>API: POST /medical-documents/{id}/complete
  API->>Q: enqueue document.validate (via outbox)
  W->>Q: receive
  W->>S3: get file
  W-->>API: status updates (DB) → SSE to user
```
## Data changes
## API changes (OpenAPI diff)
## Failure modes and handling
| Failure | Detection | Handling |
| --- | --- | --- |
## Security considerations (threat model delta)
## Observability (logs, metrics, traces, alarms)
## Rollout (flags, migration steps, backfill)
## Alternatives considered
