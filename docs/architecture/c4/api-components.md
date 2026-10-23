# C4 Level 3 - API Components (Core API modular monolith)

Status: Draft v0.1 - Owner: solution-architect (with backend-engineer) - Source: plan §8, §17, §24; ADR-0002.

Rule: modules talk only through `application` services and domain events (transactional outbox); import-linter enforces it in CI. Module names below are provisional; the authoritative list is the backend module map (TBD, owner: backend-engineer).

```mermaid
C4Component
  title Core API - Components
  Container_Ext(web, "Web app", "Next.js")
  Container_Ext(phi, "PHI Service", "FastAPI")
  ContainerDb_Ext(db, "Core DB", "PostgreSQL + pgvector")
  ContainerQueue_Ext(queue, "SQS", "Job queues")
  Container_Ext(idp, "Identity provider", "OIDC")

  Container_Boundary(api, "Core API") {
    Component(http, "HTTP layer", "FastAPI routers", "AuthN (JWT), authz dependency, Problem Details, idempotency, ETags, rate limits")
    Component(ident, "identity", "module", "Users, profiles, consents; sub claim sync")
    Component(docs, "documents", "module", "Presign flow, document state machine, duplicate check by sha256")
    Component(extr, "extraction", "module", "Run status, review and confirm commands; delegates storage to PHI Service")
    Component(clin, "clinical", "module", "Materialise confirmed findings; read model for viewer via PHI Service")
    Component(units, "units", "module", "Unit config, region catalogue (region_code), versioned")
    Component(know, "knowledge", "module", "Reviewed articles, RAG retrieval over pgvector")
    Component(share, "sharing", "module", "Share grants with scope and expiry (BR-030, BR-031)")
    Component(notif, "notifications", "module", "Email and in-app events")
    Component(outbox, "outbox", "shared kernel", "Transactional outbox and relay to SQS/EventBridge")
    Component(audit, "audit", "shared kernel", "Append-only audit events")
  }

  Rel(web, http, "JSON, SSE", "HTTPS")
  Rel(http, idp, "Validate JWT via JWKS")
  Rel(http, ident, "Calls application service")
  Rel(http, docs, "Calls application service")
  Rel(http, extr, "Calls application service")
  Rel(http, clin, "Calls application service")
  Rel(http, units, "Calls application service")
  Rel(http, know, "Calls application service")
  Rel(http, share, "Calls application service")
  Rel(docs, outbox, "DocumentUploaded event")
  Rel(extr, outbox, "FindingsConfirmed event")
  Rel(outbox, queue, "Relay", "SQS")
  Rel(extr, phi, "Health data I/O")
  Rel(clin, phi, "Health data I/O")
  Rel(share, audit, "Records access")
  Rel(notif, outbox, "Subscribes to events")
  Rel(units, db, "SQL")
  Rel(know, db, "SQL, vector search")
  Rel(ident, db, "SQL")
  Rel(share, db, "SQL")
  Rel(outbox, db, "SQL")
  Rel(audit, db, "SQL")
```

## Component notes
| Component | Rule |
| --- | --- |
| HTTP layer | Every endpoint has an authorization check and an authz test (`backend-engineer/assets/test-authz-template.py`). Foreign IDs return 404 and an audit event. |
| documents / extraction / clinical | No direct access to Clinical DB or `phi` bucket; go through PHI Service (SEC-AR-01). |
| units | `region_code` is the contract between data, API, GLB/SVG and viewer. New Unit = config + assets + schema + content (NFR-12). |
| outbox | Consumers are idempotent on `event_id`; retry with backoff, then DLQ (plan §16.4). |
| Worker | Same codebase, separate ECS service; consumes queue and does not accept user requests. |

## Open items
| Item | Owner |
| --- | --- |
| Final module list and import-linter contracts | backend-engineer |
| Policy & Consent as module vs separate service | solution-architect |
| Where the share-read path enforces Cedar policy | security-engineer |
