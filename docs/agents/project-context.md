# MediLens — Project Context (shared by every role skill)

Read this file first whenever a MediLens role skill is active and you have not yet loaded project context in this conversation. Version 1.1 (adds Part III of the plan: regulatory, clinical safety, data strategy, multimodal input, anatomy gaps, model cascade, 52-week roadmap, 9 new roles).

## Contents
1. Product in one paragraph
2. Scope by release
3. Departments, Units, Regions
4. Domain model and finding sources
5. Architecture summary (incl. secure service design)
6. Tech stack
7. Requirement code conventions
8. Key business rules (short list)
9. Quality bars (metrics, SLOs, cost)
10. Environments and data policy
11. Regulatory boundary (intended use)
12. Data strategy
13. Model cascade
14. Roadmap and gates
15. Roles and skills
16. Repository layout
17. Glossary

## 1. Product in one paragraph
MediLens is a web app that helps patients understand their own medical records. The user uploads photos/PDFs of records, digital records (text-layer PDF, DOCX, FHIR), a free-text description, or (v2) a CT series → the pipeline (pre-processing, OCR, LLM structured extraction, code normalisation, anatomical mapping) produces structured findings → the user reviews and confirms them → confirmed findings are drawn on a 3D/2D body model and organ diagrams per medical Unit, with a pre/post timeline and sourced, guard-railed explanations (RAG). The app illustrates and explains; it never diagnoses, prescribes, detects disease on images or predicts survival.

## 2. Scope by release (52-week plan, 26 sprints)
- **v1.0 (week 32):** auth + profiles, photo upload + OCR (Vietnamese + English), extraction, review screen, 2D + 3D viewer, 3 Units (Dental, Cardiology, Oncology), patient text descriptions (`patient_reported`), RAG explanations with citations, timeline, sharing, admin, audit, data-subject rights.
- **v1.5 (week 40):** digital record import (text-layer PDF, DOCX, FHIR R4 Bundle), anatomy template library (sex/age templates, `organ_status`, device glyphs, hierarchical regions), Respiratory and Nephrology–Urology Units, full model cascade with registry and cost dashboard, opt-in data donation, annotation programme.
- **v2.0 (week 52):** CT/DICOM intake with de-identification, slice viewer, organ segmentation (TotalSegmentator), patient-specific mesh + registration to template, CT report linking, distilled extraction model, FHIR export.
- **Year-2 backlog:** Surgery, Gastroenterology, Dermatology (with CV), Eye/ENT, dental X-ray numbering.
- **Non-goals:** diagnosis, prescribing, automated lesion detection or measurement on images (BR-042), HIS/EMR write-back, payments, native mobile.

## 3. Departments → Units → Regions
| Department | Units | Viewer | Key extracted data | Release |
| --- | --- | --- | --- | --- |
| Dental & Maxillofacial | General, Orthodontics, Maxillofacial surgery, Periodontics | FDI 32-tooth 2D chart + 3D jaw | tooth number (FDI 11–48, 51–85 deciduous), surface M/D/O/B/L, caries, missing, filling, implant | v1.0 |
| Internal Medicine | Cardiology (v1.0), Respiratory (v1.5), Gastro, Endocrine, Neuro | 3D heart, lungs by lobe, GI tract | ICD-10, EF%, BP, labs (LOINC), lung function | v1.0 / v1.5 / year 2 |
| Nephrology–Urology | Nephrology, Urology | kidneys, ureters, bladder | eGFR, creatinine, stones | v1.5 |
| Oncology | by organ | primary organ + nodes + metastatic sites | site, size, TNM, stage, pathology, metastases | v1.0 |
| Surgery | Ortho/Trauma, General, Neurosurgery | 3D skeleton | fracture site, laterality, procedure | year 2 |
| Dermatology | General | 2D skin map | site, size, lesion type | year 2 |

Each Unit is a versioned config: `unit_code`, `department_code`, names VI/EN, `regions[]` (region_code, standard code FMA/SNOMED, mesh_id, svg_id, laterality, parent region), `conditions[]` (ICD-10, severity scale, default region, spread-to regions), `extraction_schema` (JSON Schema), `visual_rules`, `content_refs`. Adding a Unit must not require core code changes (playbook PB-02, ≤ 3 person-days).

## 4. Domain model and finding sources
Entities (FHIR-aligned): User, PatientProfile, MedicalDocument, DocumentPage, ImagingStudy (v2), ExtractionRun, ExtractionField, Encounter, Condition, BodyFinding, Observation, Department/Unit/Region, UnitConfig, AnatomyTemplate, OrganStatus, Device, KnowledgeArticle/KnowledgeChunk, ShareGrant, Consent, AuditEvent, Outbox, Dataset, ModelConfig.

Document state machine: `uploaded → validating → rejected | queued → ocr_running → extracting → extracted → in_review → confirmed | failed` (digital records skip `ocr_running`; FHIR skips `extracting`).

**Finding Graph:** every finding carries `sourceType` = `record` (from a document), `patient_reported` (user's text), or `image_derived` (CT pipeline), plus `precision` (`exact` · `segment` · `organ` · `system` · `body_part`) and `mappingConfidence` (below 0.6 → `region = unmapped`, BR-015). Organ state per profile: `organ_status` = present · removed · absent_congenital · transplanted · implant_present, with `variant_code` and `device_type`. Conflicts resolve record > image_derived > patient_reported with a visible mismatch warning (BR-044).

## 5. Architecture summary
- Modular-monolith API (FastAPI) with modules: identity, patient, document, extraction, anatomy, clinical, knowledge, sharing, notification, audit, admin.
- Separate AI worker (Python) consuming SQS jobs: validate → preprocess → classify → ocr → extract → normalise → map → validate → (user confirm) → materialise. CT jobs (v2) run on a GPU worker that scales to zero.
- **Secure service design (plan section 24):**
  - **PHI Service** is the only component allowed to read/write clinical data (Clinical DB schema + `phi` S3 bucket).
  - **Identity Link** maps user ↔ `subject_key`; the clinical store holds no name, email or phone (SEC-AR-02).
  - **Per-record DEK** (envelope encryption under a KMS CMK) enables crypto-shredding on deletion (SEC-AR-06).
  - **Quarantine bucket** + GuardDuty Malware Protection before any parsing.
  - **AI Gateway**: PII redaction, quota/budget, cache, model routing (cascade), model allowlist, schema validation, redacted logs; IAM denies `bedrock:InvokeModel*` to every other role (SEC-AR-04).
  - **Worker subnet** has no route to NAT/Internet Gateway, only VPC endpoints (SEC-AR-03).
  - **Policies as code** (Cedar) with tests for BR-006, BR-030, BR-031 (SEC-AR-07); hash-chained audit log (SEC-AR-05).
  - Maturity: **A** (MVP, synthetic data: PHI module inside the monolith, separate schema/DB role, RLS) → **B** (before real data / G3-P: PHI Service and AI Gateway as separate ECS services with own IAM roles, per-record DEK) → **C** (hospital partners: separate PHI-vault account, PrivateLink, Verified Permissions, Macie, SIEM).
- Transactional outbox → EventBridge for domain events; EventBridge Scheduler for crons.
- AWS (ap-southeast-1): CloudFront + WAF, ALB, ECS Fargate (web, api, worker, phi-service, ai-gateway), RDS PostgreSQL 16 + pgvector (Multi-AZ prod), ElastiCache (Valkey), S3 (KMS), SQS + DLQ, Bedrock (via VPC endpoint), Cognito, Secrets Manager, KMS, AppConfig, CloudWatch/X-Ray, GuardDuty, Security Hub, Config, CloudTrail, AWS Backup. AWS HealthImaging is not offered in Singapore; v2 stores DICOM in S3 (+ Orthanc if DICOMweb is needed).
- Multi-account: management, security, log-archive, shared-services, dev, staging, prod, backup-vault (+ phi-vault at level C).

## 6. Tech stack
Frontend: Next.js (App Router) + TypeScript, Tailwind + shadcn/ui, TanStack Query, Zustand, React Hook Form + Zod, next-intl, Three.js + React Three Fiber + drei, SVG + D3, ECharts/Recharts; Cornerstone3D/OHIF for CT slices (v2).
Backend: Python 3.10, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2, asyncpg, httpx, Celery/Dramatiq (SQS broker on AWS), Cedar policies.
AI: OpenCV, PaddleOCR + VietOCR (Vietnamese printed), LLM vision on Bedrock for handwriting, Textract only for English documents (Textract does not support Vietnamese), pypdf/pdfplumber + python-docx for digital records, PyTorch, pydicom, TotalSegmentator, scikit-image (marching cubes), SimpleITK (registration), Ultralytics YOLO, SAM, bge-m3/multilingual-e5 embeddings, Langfuse/MLflow, Label Studio.
Data: PostgreSQL, S3 + Parquet/Iceberg, Glue Catalog, Athena, dbt, Prefect/Dagster, Great Expectations, Lake Formation.
DevOps: Docker, Terraform, GitHub Actions (OIDC → AWS), ECR, ECS, AppConfig.
Quality: pytest, hypothesis, Testcontainers, LocalStack, schemathesis, Vitest, Testing Library, Playwright, axe-core, k6, Storybook.
Security: Semgrep, CodeQL, Trivy, Checkov, gitleaks, OWASP ZAP, Inspector.

## 7. Requirement code conventions
- `BR-xxx` business rule · `FR-xxx` functional · `NFR-xx` non-functional · `SEC-<area>-xx` security (ID, AZ, DP, AP, AI, IN, LG, AR) · `DAT-xx` data · `DE-xx` data engineering · `BE-API-xx` backend API · `FE-VW-xx` / `FE-SEC-xx` frontend · `OPS-xx` operations · `UN-xxx` user need · `CS-xxx` clinical safety requirement · `HZ-xxx` hazard · `VAL-xxx` validation evidence · `LIC-xxx` licence register entry · `DS-xxx` dataset · `US-xxx` user story · `TC-xxx` test case · `ADR-xxx` decision · `RDR-xxx` regulatory decision record · `R-xx` risk · `CR-xxx` change request.
- Requirement strength follows RFC 2119: MUST / SHOULD / MAY.
- Traceability (design controls): UN → BR/FR/NFR/SEC/CS → design output → TC (verification) → VAL (validation). Every BR traces to ≥ 1 US and ≥ 1 TC.

## 8. Key business rules (short list — full catalog in BA skill)
- BR-002 consent before first upload; re-consent on terms change.
- BR-006 RBAC + ownership; Admin cannot read PHI without break-glass.
- BR-010/011 formats JPG/PNG/HEIC/PDF, ≤ 20 MB, ≤ 30 pages; reject blurry/low-res images.
- BR-012 field confidence < 0.7 must be confirmed by the user.
- BR-013 only `confirmed` data appears on viewer/timeline.
- BR-015 unmappable → `region = unmapped`, never guess.
- BR-020 severity palette green/yellow/orange/red/purple, always with text label.
- BR-021 metastasis shown only when the record states it; "possible spread" is separate educational content.
- BR-022/023 LLM answers only from approved knowledge + user's own data; no doses, no medication changes, no survival prognosis; emergencies → 115.
- BR-030/031 sharing is scoped, time-limited (default 7, max 90 days), revocable, signed-in recipients only.
- BR-032 export and delete (soft now, hard after 30 days).
- BR-034 no training on user data without separate opt-in.
- BR-035 every PHI read/write audited, append-only, ≥ 3 years.
- BR-040 `patient_reported` findings get no ICD-10 code and no severity colour; always labelled "you described".
- BR-041 emergency signs in a text description → show 115 before any other content.
- BR-042 CT images only build illustrative anatomy; no automated detection or measurement of lesions (stays outside SaMD scope).
- BR-043 DICOM is de-identified before any processing; only the user can re-download the original.
- BR-044 conflicting sources: record > image_derived > patient_reported, with a mismatch warning.
- BR-045 text-layer digital records are extracted directly (no OCR); valid FHIR maps without the LLM.

## 9. Quality bars
- AI (MVP → target): field F1 ≥ 0.80 → 0.92; printed CER ≤ 5% → 2%; region accuracy ≥ 0.85 → 0.95; FDI tooth accuracy ≥ 0.90 → 0.98; ICD-10 top-1 ≥ 0.75 → 0.90; RAG faithfulness ≥ 0.85 → 0.95; hallucination ≤ 5% → 1%; guardrail block ≥ 95% with false block ≤ 10%; p95 processing ≤ 3 min → 60 s; CT registration error < 15 mm.
- Cost: AI ≤ 0.10 USD/document (MVP) → ≤ 0.03 (target); worked example with the cascade ≈ 0.01 USD/document; cache hit ≥ 60% on fixed prompt parts; escalation to Tier L ≤ 15%.
- SLOs: API availability 99.5%/month; API p95 ≤ 300 ms, p99 ≤ 1 s; 95% documents processed < 2 min; 5xx ≤ 0.5%.
- Frontend: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1; 3D ≥ 50 FPS desktop / ≥ 30 FPS mobile; model ≤ 5 MB.
- Quality: BE coverage ≥ 80%, FE ≥ 70%, 100% endpoint authorization tests; 0 open S1/S2 at release; 0 High vulns past SLA; WCAG 2.2 AA.
- Data: golden set ≈ 200 documents per reported stratum (n = z²·p(1−p)/e², p = 0.85, e = ±5%); ≥ 30 per sub-group for bias checks; label agreement Cohen's kappa ≥ 0.8.
- Recovery: RPO ≤ 24 h (target 5 min via PITR), RTO ≤ 4 h.

## 10. Environments and data policy
local (Docker Compose, LocalStack) → dev → staging → prod. Only synthetic or licensed public data outside prod, and no real patient data anywhere before gate G3-P. Data classes: C4 PHI, C3 PII, C2 internal, C1 public, C0 synthetic. Never put PHI/PII in logs, traces, analytics, URLs, prompts to external providers (redact first), or test fixtures. Privacy law: Law on Personal Data Protection 91/2025/QH15 + Decree 356/2025/ND-CP (both in force 1 Jan 2026; Decree 356 replaced Decree 13/2023): explicit consent for health data, DPIA and overseas-transfer impact assessment (OTIA) within 60 days of starting processing/transfer, breach notice to the authority within 72 hours of detection.

## 11. Regulatory boundary (intended use)
Software used for a medical purpose such as diagnosis or monitoring can be a medical device in Vietnam (Decree 98/2021/ND-CP as amended by Decree 07/2023 and Decree 04/2025; classification A–D under Circular 05/2022). MediLens keeps v1 in an illustrative/educational scope: "helps users review and understand information already written in their own health records, with illustrations and sourced educational content; it does not diagnose, recommend treatment or analyse images to detect disease". Any feature crossing that line (e.g., lesion detection on CT) needs a new Regulatory Decision Record (gate G0-R) and expert advice. Forbidden claim words in UI, marketing and LLM output: "chẩn đoán", "phát hiện bệnh", "thay thế bác sĩ" (diagnose, detect disease, replaces your doctor). Circular 13/2025/TT-BYT drives hospital EMR adoption but defines no patient API, so MediLens ingests what the user already holds. References for practice: IMDRF SaMD, IEC 62304, ISO 14971, IEC 62366, ISO 13485.

## 12. Data strategy
Four tiers, lowest risk first; move up only after passing the previous tier's gate: (1) self-generated synthetic records → (2) licensed public data (check training and product-use rights; NC = non-commercial, SA = share-alike, DUA = no redistribution) → (3) opt-in user donations (separate consent, de-identified, withdrawable) → (4) partner hospitals (data sharing agreement, partner ethics approval, DPIA, OTIA if processed abroad). Every source enters the **License Register** before download; every dataset has an immutable version, checksum, Dataset Card and lineage to the models that used it. Gate **G1-D** before any training/fine-tuning. Learning curves (10/25/50/100%) decide whether more training data is needed.

## 13. Model cascade
Rule/cache → Tier S (small/cheap) → Tier M → Tier L → human review, routed by the AI Gateway on calibrated confidence. OCR and CT segmentation run on self-hosted open models (zero tokens). Levers: prompt caching, batch inference (~50% cheaper) for non-urgent work, semantic cache for explanations, per-user quotas, distillation to a small model once enough licensed, confirmed data exists. Every configuration (provider, pinned model ID, prompt version, thresholds) lives in the model registry with a Model Card; quarterly bake-off; fallback provider switchable via AppConfig in < 5 minutes.

## 14. Roadmap and gates
7 phases / 26 sprints × 10 working days / 20 hours per week: P0 Initiation & Discovery (S01–S02) · P1 Foundation (S03–S05) · P2 Build MVP (S06–S11) · P3 Hardening (S12–S14) · P4 Beta & Launch v1.0 (S15–S16) · P5 Hypercare & v1.5 (S17–S20) · P6 v2.0 CT (S21–S26). Gates: G0 Discovery and G0-R Regulatory (S02) · G1 Architecture ready and G1-D Data licence (S05) · G2 Feature complete (S11) · G2-CS Clinical safety (S13) · G3 Release gate and G3-P External pentest (S14) · G4 Launch review (S16) · G5-H Hypercare exit (S18) · G5 Release v1.5 (S20) · G0-R re-run for CT (S21) · G1-D round 2 before fine-tuning (S22) · G6 Release v2.0 (S26). Day-level plan: `MediLens_Sprint_Plan_52w.xlsx`.

## 15. Roles and skills
`medilens-orchestrator` routes work. Role skills (all prefixed `medilens-`): product-manager, business-analyst, ux-ui-designer, solution-architect, ai-ml-engineer, data-engineer, backend-engineer, frontend-engineer, cloud-devops-engineer, security-engineer, qa-engineer, qc-release-gatekeeper, sre-operations, and from Part III clinical-safety-officer ★, regulatory-privacy-officer ★, clinical-informaticist, data-curator ★, mlops-engineer, medical-imaging-engineer, 3d-medical-artist, technical-writer, support-success. ★ = the learner plays the role, but a real qualified person must sign before real data or public launch. Blocking roles: Clinical Safety (G2-CS), Regulatory & Privacy (G0-R, G1-D), Security (G3-P) and QC (G3) can each stop a release.

## 16. Repository layout
```
medilens/
├── apps/web  apps/api  apps/worker  apps/phi-service  apps/ai-gateway
├── packages/anatomy-assets  packages/api-client  packages/design-system
├── ml/datasets  ml/eval  ml/notebooks  ml/registry
├── imaging/         (DICOM de-id, segmentation, mesh, registration — v2)
├── data/            (dbt, flows, license-register.csv, dataset cards)
├── infra/           (terraform, docker-compose)
├── regulatory/      (intended use, RDR, claims review, AI impact assessments)
├── safety/          (clinical risk plan, hazard log, safety case, validation)
├── docs/            (brd, srs, adr, security, runbooks, architecture, user guide)
└── .github/workflows
```

## 17. Glossary
- PHI: protected health information (here: any health data linked to a person).
- Unit: a medical sub-specialty with its own viewer/config.
- Region: an anatomical area addressable on the viewer (`region_code`); regions form a tree (system → organ → sub-region).
- Finding / BodyFinding: a lesion or abnormality located on a Region; has `sourceType`, `precision` and `mappingConfidence`.
- `subject_key`: pseudonymous key linking identity to clinical data.
- DEK: data-encryption key per record; deleting it crypto-shreds the record.
- Golden set: frozen labelled evaluation set, never used for tuning.
- Hazard log / Safety Case: ISO 14971-style record of clinical hazards, controls and residual risk; signed by the Clinical Safety Officer.
- RDR: Regulatory Decision Record (intended use, device/non-device reasoning, references, review date).
- OTIA: overseas transfer impact assessment under the PDPL.
- Break-glass: logged, time-limited emergency access.
- DSR: data subject request (access, correction, deletion, consent withdrawal) under Vietnam's Law on Personal Data Protection 91/2025/QH15 (in force 1 Jan 2026) and its guiding Decree 356/2025/ND-CP, which replaced Decree 13/2023.
