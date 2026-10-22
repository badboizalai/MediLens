# Solution Architecture Document (arc42) - MediLens

Status: Draft v0.1 (2026-10-23) - Owner: solution-architect. Unknowns are marked TBD with an owner. Sources: project plan §8, §13, §16, §20, §24; ADRs in `docs/architecture/adr/`; NFR catalog in the solution-architect skill.

## 1. Introduction and goals
MediLens lets patients upload records (photo, PDF, digital, text), extracts structured findings with OCR + LLM, lets the user review them, then colours a 2D/3D body viewer by `region_code`. It illustrates and explains; it never diagnoses, doses or gives prognosis (BR-042).

**Top quality goals**
| # | Goal | NFRs |
| --- | --- | --- |
| 1 | Privacy and security of health data | NFR-08, NFR-09 |
| 2 | Correctness and traceability of extracted findings (user confirms) | NFR-06, NFR-14 |
| 3 | Low cost for a solo operator | NFR-15 |
| 4 | Extensibility: new Unit is config-only | NFR-12 |
| 5 | Availability and timely processing | NFR-01, NFR-04 |

**Stakeholders**: patients/caregivers (use), clinicians (shared view), operator (solo developer), regulatory/privacy officer, clinical safety officer, security engineer (blocking gates G0-R, G1-D, G2-CS, G3-P).

## 2. Constraints
- Technical: Python 3.10 / FastAPI, Next.js, PostgreSQL 16 + pgvector, AWS ap-southeast-1 (provisional, ADR-0004); Textract has no Vietnamese; HealthImaging unavailable in Singapore.
- Organisational: one-person team (ADR-0001); monorepo; skills change via PR.
- Legal: Law 91/2025/QH15 and Decree 356/2025/ND-CP (explicit consent, DPIA, overseas-transfer assessment, 72 h breach notice); medical-device rules Decree 98/2021 as amended (intended-use limits, BR-042).
- Data: no real patient data anywhere before gate G3-P; synthetic data only in repo, dev, staging.

## 3. Context and scope
See `docs/architecture/c4/context.md`. External actors: patient, clinician, operator. External systems: identity provider (Cognito or Keycloak, TBD), Amazon Bedrock, optional Textract (English), SES.

## 4. Solution strategy
| Decision | Choice | ADR |
| --- | --- | --- |
| Repository | Monorepo with in-repo skills | ADR-0001 |
| Architecture style | Modular monolith (FastAPI) + async AI worker; PHI Service and AI Gateway separate for trust boundaries | ADR-0002 |
| OCR | Hybrid: local PaddleOCR/VietOCR first, Bedrock vision on low confidence, behind `OcrProvider` | ADR-0003 |
| Region / LLM | ap-southeast-1 provisional; Bedrock via VPC endpoint through AI Gateway only | ADR-0004 |
| Integration | Transactional outbox, SQS + DLQ, idempotent consumers | plan §16.4 |
| Data separation | `subject_key` pseudonym, per-record DEK, no internet for AI zone | plan §24 |

Note: ADR files are numbered 0001-0004 but files 0002-0004 carry plan-backlog ids (ADR-001, ADR-006, ADR-012) in their titles. TBD: renumber or add a mapping (owner: solution-architect). Their status is "Proposed"; this SAD treats them as the working decisions until accepted.

## 5. Building block view
- Level 1: `docs/architecture/c4/context.md`
- Level 2: `docs/architecture/c4/containers.md` (web, api, worker, ai-gateway, phi-service, PostgreSQL, Redis/SQS, S3, identity provider, LLM/OCR)
- Level 3 (API): `docs/architecture/c4/api-components.md`
- Level 3 (worker): TBD (owner: ai-ml-engineer; stages: quality check, OCR, extraction, normalisation, region mapping).

## 6. Runtime view
1. **Upload and process**: web asks API for presigned PUT to quarantine S3 (5 min) -> malware scan and magic-byte check -> `POST /documents/{id}/complete` -> API writes `DocumentUploaded` to outbox -> SQS -> worker runs OCR/extraction (LLM only via AI Gateway) -> results written through PHI Service -> progress via SSE (202 async request-reply).
2. **Review and confirm**: user corrects fields; confirm triggers `clinical.materialize`, creating conditions, body findings and observations.
3. **View**: web calls `/units/{code}/config` and `/findings`; API reads findings through PHI Service (policy, decrypt, audit, minimal DTO); viewer colours regions by `region_code`.
4. **Explain (RAG)**: retrieval over reviewed knowledge articles (pgvector), LLM through AI Gateway, citations, guardrails. TBD detailed sequence (owner: ai-ml-engineer).
5. **Share**: owner creates a grant (scope, expiry); clinician reads within scope; every read audited. TBD sequence (owner: backend-engineer).
6. **Delete account**: saga with compensable steps - revoke sessions, delete DEKs, delete S3 versions, delete Identity Link row, delete analytics rows, confirm. TBD DSR runbook (owner: data-engineer).

## 7. Deployment view
Account structure (plan §7): management, security, log-archive, shared-services, dev, staging, prod, backup-vault (+ phi-vault at maturity level C). Region ap-southeast-1 as a single Terraform variable.

| Aspect | local | staging | prod |
| --- | --- | --- | --- |
| Purpose | Development | Pre-release, UAT, load tests | Real users (only after G3-P) |
| Runtime | Docker Compose (`make up`), LocalStack for AWS | ECS Fargate, like prod, single-AZ allowed | ECS Fargate (web, api, worker, phi-service, ai-gateway), Multi-AZ |
| Data stores | Postgres, Redis, LocalStack S3/SQS | RDS PostgreSQL, ElastiCache, S3, SQS | RDS Multi-AZ + PITR, ElastiCache, S3 (KMS), SQS + DLQ |
| Identity | Local OIDC stub (TBD, owner: backend-engineer) | Cognito or Keycloak (TBD) | Same as staging |
| LLM | Fake provider / recorded fixtures | Bedrock via VPC endpoint, synthetic data | Bedrock via VPC endpoint |
| Data | Synthetic seed | Large synthetic set | Real |
| Deploy | Manual | Auto on release tag | Manual approval, blue/green |

(A `dev` environment sits between local and staging: auto-deploy on merge, synthetic, off at night.)
Edge: CloudFront + WAF -> ALB -> ECS. AI worker subnet has no NAT/IGW route; VPC endpoints for S3, SQS, KMS, Bedrock only. Observability: CloudWatch, X-Ray, GuardDuty, Security Hub, Config, CloudTrail, AWS Backup. Feature flags via AppConfig. Maturity A/B/C staging of PHI isolation per plan §24.5. TBD: network CIDR plan and VPC endpoint list (owner: cloud-devops-engineer).

## 8. Cross-cutting concepts
**Security and PHI boundary**
- Only the PHI Service reads or writes C4 data (SEC-AR-01); Clinical DB holds no email/name/phone, only `subject_key` (SEC-AR-02); identity map in a separate DB with its own CMK.
- Authorization on every endpoint with a test; ownership failures return 404 plus audit event; policies as code (Cedar) for BR-006, BR-030, BR-031 (SEC-AR-07).
- Every LLM call via AI Gateway: PII redaction, quota, cache, allowlist; IAM denies direct Bedrock calls elsewhere (SEC-AR-04).
- Uploads: quarantine bucket, malware scan, sandboxed parsing (SEC-AR-09).
- Keys: `kms/phi`, `kms/identity`, `kms/app`, `kms/logs`; per-record DEK for crypto-shredding.
- Data classes C0-C4; no PHI/PII in logs, traces, URLs, analytics, fixtures or unredacted prompts.

**Authorization model**: role + ownership + share + consent; break-glass admin access 1 h with reason and alert.

**Observability**: OpenTelemetry/ADOT; every request carries a traceId (NFR-13); structured logs without PHI; every alarm has a runbook; SLO dashboards (API 99.5%), queue depth and DLQ alarms, AI cost per document and escalation rate. TBD alarm catalog (owner: sre-operations).

**i18n**: full VI + EN (NFR-16) with next-intl; bilingual medical content model (`name_vi`, `name_en`); new locale without code change; medical wording reviewed by clinical safety officer. TBD locale fallback rules (owner: frontend-engineer).

**Error handling and resilience**: Problem Details errors; retry with backoff and jitter then DLQ; idempotency key `event_id`; circuit breaker with provider fallback; bulkhead of OCR and LLM queues; provider adapters for OCR, LLM, email.

**Configuration and flags**: Unit config versioned in `unit_configs`; AppConfig flags; secrets in Secrets Manager.

**Data model**: main tables in plan §8.2; UUIDv7 keys, soft delete, RLS by `profile_id`, field-level encryption for sensitive fields; `region_code` is the contract between data, API, assets and viewer.

## 9. Architecture decisions
| ADR | Title | Status |
| --- | --- | --- |
| [0001](adr/0001-monorepo-and-skill-pack.md) | Monorepo with skill pack | Accepted |
| [0002](adr/0002-modular-monolith.md) | Modular monolith + AI worker | Proposed |
| [0003](adr/0003-hybrid-ocr.md) | Hybrid OCR | Proposed |
| [0004](adr/0004-region-and-bedrock.md) | Region and Bedrock availability | Proposed |

Backlog still open (plan §16.3): identity provider (Cognito vs Keycloak), queueing detail, vector store (pgvector recommended), 3D format (glTF/GLB), tenancy (single-tenant B2C), FHIR alignment, frontend rendering. Owner: solution-architect.

## 10. Quality requirements
Full NFR-01..NFR-17 table: solution-architect `references/nfr-catalog.md` and plan §16.1. Key targets: API 99.5%/month; read p95 <= 300 ms; 95% of documents < 2 min; RPO <= 24 h (5 min PITR target), RTO <= 4 h; cost <= 100 USD/month at 100 MAU and AI <= 0.10 USD/doc; WCAG 2.2 AA.

**Quality scenarios**
| ID | Attribute | Scenario (source, stimulus, response, measure) |
| --- | --- | --- |
| QS-1 | Availability | One AZ loses connectivity at peak; API keeps serving with < 1% 5xx, self-heals in 5 min, no in-flight document lost (messages return to queue) |
| QS-2 | Security | User A changes a URL ID to B's document; system returns 404, writes an audit event, alerts at >= 10 attempts/min |
| QS-3 | Modifiability | Team adds Nephrology-Urology Unit with config, assets, extraction schema and content in <= 3 person-days, no core API redeploy |
| QS-4 | Cost | Traffic grows 5x in a day; AI spend stays within daily budget via per-user quotas and circuit breakers |
| QS-5 | Durability | Worker crashes mid-OCR; message reappears after visibility timeout and is reprocessed idempotently; 0 documents lost, 0 duplicate side effects |
| QS-6 | Portability | OCR or LLM provider replaced behind its adapter in <= 2 days with eval harness passing |

## 11. Risks and technical debt
| Risk | Mitigation | Owner |
| --- | --- | --- |
| Bedrock models not available in-region (ADR-0004 VERIFY items) | Prefer another model over cross-region inference; region is one variable | solution-architect |
| Overseas-transfer assessment coverage | Legal reading of Decree 356/2025 | regulatory-privacy-officer |
| Handwriting accuracy of local OCR | Golden-set measurement, escalate low confidence | ai-ml-engineer |
| Module boundary erosion in monolith | import-linter in CI; revisit ADR-0002 triggers | backend-engineer |
| Identity provider undecided | Write ADR before auth implementation | solution-architect |
| ADR numbering mismatch (see section 4) | Renumber or map | solution-architect |

## 12. Glossary
- **PHI / C4**: health data; **PII / C3**: identity data (classes in project context).
- **region_code**: stable code of an anatomical region shared by data, API, assets and viewer.
- **Unit**: a clinical department module driven by config (dental, cardiology, oncology...).
- **subject_key**: pseudonymous key linking clinical data to a user only via Identity Link DB.
- **Outbox**: table written in the same transaction as state, relayed to the queue.
- **DEK / CMK**: per-record data key / KMS customer-managed key.
- **BR-042**: the app illustrates and explains; never diagnoses, doses or gives prognosis.
- **G0-R, G1-D, G2-CS, G3-P**: regulatory, data, clinical safety and privacy/security gates.
