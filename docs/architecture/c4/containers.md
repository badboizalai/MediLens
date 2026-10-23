# C4 Level 2 - Containers

Status: Draft v0.1 - Owner: solution-architect - Source: plan §8, §16, §19, §24; ADR-0002 (modular monolith + worker), ADR-0004.

```mermaid
C4Container
  title MediLens - Containers
  Person(user, "Patient / caregiver / clinician")
  System_Ext(idp, "Cognito / Keycloak (TBD)", "OIDC identity provider")
  System_Ext(llm, "Amazon Bedrock", "LLM and vision LLM")
  System_Ext(ocrx, "Textract (optional, EN)", "Cloud OCR")

  System_Boundary(edge, "Zone: edge / public") {
    Container(web, "Web app", "Next.js, TypeScript", "UI, upload, review screen, 3D/2D viewer (client-only)")
  }

  System_Boundary(app, "Zone: application (private subnets)") {
    Container(api, "Core API / BFF", "FastAPI modular monolith", "AuthN/Z, rate limits, Unit config, knowledge, sharing metadata, SSE; no PHI rights")
    ContainerDb(cache, "Cache", "Redis / Valkey (ElastiCache)", "Sessions, config cache, rate limits; no PHI")
    ContainerDb(coredb, "Core DB", "PostgreSQL 16 + pgvector", "Schemas core and policy; knowledge vectors")
    ContainerQueue(queue, "Job queues", "SQS + DLQ (EventBridge for domain events)", "Separate OCR and LLM queues; outbox publishes here")
  }

  System_Boundary(phiz, "Zone: PHI (KMS phi / identity keys)") {
    Container(phi, "PHI Service", "FastAPI", "Only gate to C4 data: policy check, field decryption, audit, minimal DTOs")
    ContainerDb(clin, "Clinical DB", "PostgreSQL (RLS)", "Documents, extractions, findings; keyed by subject_key only")
    ContainerDb(idl, "Identity Link DB", "PostgreSQL", "user_id to subject_key map, separate CMK")
    Container(s3, "Object storage", "S3 phi + quarantine buckets", "Record files; quarantine has 24 h TTL and malware scan")
  }

  System_Boundary(aiz, "Zone: AI (no internet route)") {
    Container(worker, "AI Worker", "Python, PaddleOCR/VietOCR", "Quality check, OCR, extraction, normalisation, region mapping")
    Container(gw, "AI Gateway", "Python", "PII redaction, quotas, cache, model allowlist and routing, circuit breaker, cost metering")
  }

  Rel(user, web, "Uses", "HTTPS via CloudFront + WAF")
  Rel(user, s3, "Presigned PUT upload to quarantine", "HTTPS")
  Rel(web, api, "JSON, SSE", "HTTPS")
  Rel(web, idp, "Login", "OIDC")
  Rel(api, idp, "Validates JWT (JWKS)", "HTTPS")
  Rel(api, cache, "Sessions, cache", "TLS")
  Rel(api, coredb, "SQL", "TLS")
  Rel(api, phi, "Reads and writes health data on behalf of principal", "mTLS/IAM")
  Rel(api, queue, "Jobs via transactional outbox", "SQS")
  Rel(phi, clin, "SQL", "TLS")
  Rel(phi, idl, "Resolve subject_key", "TLS")
  Rel(phi, s3, "Moves clean files, reads", "KMS")
  Rel(worker, queue, "Consumes", "VPC endpoint")
  Rel(worker, s3, "Reads files", "VPC endpoint")
  Rel(worker, phi, "Writes results", "own IAM role")
  Rel(worker, gw, "LLM and vision calls", "internal")
  Rel(gw, llm, "Redacted prompts", "Bedrock VPC endpoint")
  Rel(gw, ocrx, "English pages, if adopted", "VPC endpoint")
```

## Container responsibilities and trust
| Container | Responsibility | Data class | Trust zone | Key control |
| --- | --- | --- | --- | --- |
| Web app | UI, viewer, i18n VI/EN | C2 in browser; C4 only rendered | Public | CSP, HttpOnly cookies, no PHI in URLs/logs |
| Core API / BFF | Non-PHI logic, orchestration, SSE | C1-C2 | App | Authz on every endpoint + test; no DB/IAM rights to PHI (SEC-AR-01) |
| PHI Service | Sole reader/writer of C4 | C4 | PHI | Policy per request, field encryption, audit |
| AI Worker | OCR and extraction pipeline | C4 in memory | AI | Subnet without NAT/IGW (SEC-AR-03); VPC endpoints only |
| AI Gateway | Every LLM/OCR-cloud call | C4 to C2 after redaction | AI | IAM denies `bedrock:InvokeModel*` elsewhere (SEC-AR-04) |
| Core DB | Non-PHI data, pgvector | C1-C2 | App | RLS, KMS app key |
| Clinical DB | Health data by `subject_key` | C4 | PHI | No email/name/phone (SEC-AR-02); KMS phi; per-record DEK |
| Identity Link DB | `user_id` to `subject_key` | C3 | PHI | Separate CMK; PHI Service only |
| Redis/Valkey | Sessions, cache, throttles | C2 | App | No PHI |
| SQS + DLQ | Async jobs; at-least-once; idempotency key `event_id` | C2 (ids only) | App | Encrypted with KMS app key |
| S3 | Files; quarantine then phi | C4 | PHI | Presigned PUT 5 min, malware scan, versioned |
| Identity provider | Login, tokens | C3 | External/managed | TBD Cognito vs Keycloak |
| LLM/OCR providers | Extraction, vision | Redacted only | External | Gateway only; in-region |

## Notes
- Per ADR-0002 API and worker are separate ECS services from one codebase; PHI Service and AI Gateway are separate deployables because trust boundaries differ, not scale.
- Maturity level A (synthetic-only MVP) may host PHI Service as a module with own schema/role and the Gateway as a library; level B (before G3-P) splits them as drawn (plan §24.5).
- Policy & Consent, Audit and De-ID services (plan §24.1) are not drawn separately yet. TBD whether they are modules in Core API or deployables (owner: solution-architect, with security-engineer).
- Valkey vs Redis: plan names ElastiCache (Valkey); both speak the Redis protocol. The plan text also says the worker pulls jobs from Redis (§8) while §16.3 recommends SQS; this SAD follows SQS (TBD confirm in ADR-005, owner: solution-architect).
