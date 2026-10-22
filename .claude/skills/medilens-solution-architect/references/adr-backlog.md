# ADR Backlog

| ADR | Decision | Status | Chosen | Main alternatives | Revisit when |
| --- | --- | --- | --- | --- | --- |
| 001 | Architecture style | Accepted | Modular monolith + AI worker | Microservices, plain monolith | > 3 developers or independent scaling needs |
| 002 | Backend language/framework | Accepted | Python 3.12 + FastAPI | NestJS, Spring Boot | — |
| 003 | Identity provider | Proposed | Cognito (managed) | Keycloak (learning OIDC deeply), Auth0 | Need for custom flows Cognito cannot do |
| 004 | Compute | Accepted | ECS Fargate | App Runner, Lambda, EKS | Need K8s ecosystem or GPU |
| 005 | Messaging | Accepted | SQS (jobs) + EventBridge (events, scheduler) | Redis/Celery broker, RabbitMQ | Complex routing needs |
| 006 | OCR | Accepted | PaddleOCR/VietOCR primary; Bedrock vision for handwriting; Textract only English | Google Document AI, Azure DI | Accuracy plateau below target |
| 007 | LLM provider | Proposed | Amazon Bedrock | Direct provider APIs, self-hosted | Model unavailable in region or cost |
| 008 | Vector store | Accepted | pgvector | OpenSearch, Bedrock Knowledge Bases | > 1M chunks or hybrid search needs |
| 009 | 3D format | Accepted | glTF 2.0 / GLB + Draco/Meshopt | FBX, USDZ | — |
| 010 | Event integration | Accepted | Transactional outbox | Dual write, CDC | — |
| 011 | Tenancy | Accepted | Single-tenant B2C; `org_id` reserved | Multi-tenant B2B | B2B pilot |
| 012 | Region | Proposed | ap-southeast-1 Singapore | ap-southeast-7 Thailand | Model availability, data-residency rules |
| 013 | Health data standard | Accepted | FHIR-aligned names; FHIR export v2 | Custom only | Hospital integration |
| 014 | Frontend rendering | Accepted | Next.js hybrid; viewer client-only | SPA | — |
| 015 | IaC | Accepted | Terraform | CDK, Pulumi | — |
| 016 | PHI boundary | Accepted | PHI Service + Identity Link (`subject_key`); maturity A → B before real data | Shared schema with RLS only | Hospital partner (→ level C, separate account) |
| 017 | LLM egress | Accepted | AI Gateway (redaction, quota, cache, cascade, allowlist); IAM deny elsewhere | Direct SDK calls per module | Provider adds a native gateway feature |
| 018 | Encryption for deletion | Accepted | Per-record DEK envelope encryption + crypto-shredding | Hard delete + backup purge | Backup tooling changes |
| 019 | Authorization engine | Proposed | Cedar policies in-process (Verified Permissions at level C) | Hand-written checks, OPA | Policy count > 100 or B2B |
| 020 | Imaging storage | Proposed | S3 + optional Orthanc for DICOMweb (HealthImaging not in ap-southeast-1) | HealthImaging in another region (needs OTIA) | Hospital integration |
| 021 | Model operations | Accepted | Cascade S → M → L with registry, Model Cards, AppConfig fallback | Single mid-tier model | Escalation > 15% or new model family |
| 022 | Digital record import | Proposed | Text layer first (BR-045), DOCX sanitised, FHIR mapped without LLM | OCR everything | Partner provides structured feeds |
