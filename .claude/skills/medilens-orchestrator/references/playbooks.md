# Cross-role Playbooks

Each step names the owner skill, the deliverable and the gate that must pass before the next step.

## Contents
- PB-01 New feature end-to-end
- PB-02 Add a new medical Unit
- PB-03 Change an AI model or prompt
- PB-04 Production incident
- PB-05 Release to production
- PB-06 Data subject request (export/delete)
- PB-07 New third-party provider
- PB-08 Security vulnerability report
- PB-09 Schema change touching analytics
- PB-10 Quarterly maintenance cycle
- PB-11 Add a new input type
- PB-12 Acquire and onboard a dataset
- PB-13 Reduce AI cost / change model routing
- PB-14 Clinical safety case and gate G2-CS
- PB-15 Launch hypercare and gate G5-H
- PB-16 Feature near the regulatory boundary (e.g., CT)

## PB-01 New feature end-to-end
| # | Owner | Deliverable | Gate |
| --- | --- | --- | --- |
| 1 | product-manager | Feature brief: problem, metric, priority score | Priority accepted into backlog |
| 2 | business-analyst | Stories (INVEST) + Gherkin AC + linked BR | Definition of Ready met |
| 3 | ux-ui-designer | Design spec (states, copy, a11y notes) | Usability check or heuristic review done |
| 4 | solution-architect | Design note / ADR if new pattern or tech | ADR accepted |
| 5 | security-engineer | Threat model delta + SEC requirements | No unmitigated High threat |
| 6 | qa-engineer | Test cases from AC (written before code) | Each AC has ≥ 1 test |
| 7 | backend-engineer | API + migration + tests + OpenAPI | CI green, authz tests pass |
| 8 | frontend-engineer | UI + tests + Storybook | CI green, a11y 0 serious |
| 9 | ai-ml-engineer (if AI) | Prompt/schema/eval | Golden set not worse |
| 10 | cloud-devops-engineer | Infra changes + deploy to staging | Smoke tests pass |
| 11 | qc-release-gatekeeper | Exploratory session + readiness | GO |
| 12 | sre-operations | Dashboards/alerts/runbook for the feature | Alert has runbook |

## PB-02 Add a new medical Unit (example: Nephrology–Urology)
1. business-analyst — Unit brief: conditions in scope (ICD-10 list), fields to extract, glossary terms, BR changes (e.g. BR-017 mapping).
1b. clinical-informaticist — region tree (codes, parents, laterality, precision), code mapping table (ICD-10/LOINC), FHIR mapping notes.
2. ux-ui-designer — Unit visual spec: regions, legend, detail panel copy, severity mapping.
3. ai-ml-engineer — `extraction_schema` JSON Schema, prompt section, mapping rules text → region_code, ≥ 30 synthetic labelled documents, eval run.
4. data-engineer — reference data (codes, region catalog) via data migration; catalog entries.
5. 3d-medical-artist — GLB/SVG assets with names = region_code, budgets met (`glb_budget_check.py`, `svg_region_check.py`), licences recorded.
5b. frontend-engineer — plugin registration; `check_glb_regions` passes; performance budget on the test phone.
6. backend-engineer — publish `unit_config` version (config only, no core change); seed migration.
7. qa-engineer — Unit test cases, visual regression baselines, eval in CI.
8. clinical-safety-officer — hazard-log delta for the Unit, display review, KnowledgeArticles approved; technical-writer — VI/EN strings and help pages.
9. product-manager — feature flag rollout plan (AppConfig) and success metric.
Gate: NFR-12 — total effort ≤ 3 person-days and zero core-code diffs; if violated, solution-architect opens an ADR to fix extensibility.

## PB-03 Change an AI model or prompt
1. ai-ml-engineer — hypothesis + change in a branch; mlops-engineer — registry entry (MC id) and Model Card updated.
2. ai-ml-engineer — run golden set + red-team set; compare to baseline per Unit.
3. security-engineer — if provider changes: vendor assessment, data residency, redaction still effective.
4. qa-engineer — CI eval gate (F1 drop ≤ 1 point per Unit, guardrails ≥ threshold).
5. mlops-engineer — promotion checklist: shadow → 10% canary → 100% via AppConfig; cost model and thresholds re-tuned. regulatory-privacy-officer — AI impact assessment if the use case, data or provider changes.
6. sre-operations — watch correction rate, latency, cost for 7 days; rollback criteria defined.
7. product-manager — record decision in decision log.

## PB-04 Production incident
1. sre-operations — declare SEV, open incident channel/notes, assign roles (you hold all), start timeline.
2. If PHI exposure suspected → security-engineer takes command (SEC-LG-04, 72-hour notification clock).
3. sre-operations — mitigate first (rollback, flag off, scale, block), then diagnose.
4. Owner skill (backend/frontend/ai/devops) — fix with tests.
5. sre-operations — post-mortem within 48 h (blameless, 5 Whys, action items with dates).
6. product-manager — action items into backlog with priority; risk register updated.

## PB-05 Release to production
1. product-manager — release scope frozen, release notes draft.
2. qa-engineer — full regression, performance smoke, AI eval.
3. security-engineer — security sign-off checklist (no High open, SBOM, image scan clean).
3b. clinical-safety-officer — Safety Case current (RG-15); regulatory-privacy-officer — RDR current and claims lint clean (RG-16, RG-17); data-curator — G1-D status for models in the release (RG-19); technical-writer — i18n check and release notes (RG-21, RG-14).
4. qc-release-gatekeeper — `scripts/release_gate.py` on metrics JSON (RG-01…RG-21) → GO/NO-GO report.
5. cloud-devops-engineer — migration on staging copy, blue/green deploy, smoke tests.
6. sre-operations — 30-minute post-deploy watch; rollback if SLO burn rate > threshold.
7. product-manager — publish release notes, close sprint.

## PB-06 Data subject request
1. backend-engineer — verify identity (re-auth + MFA), log request, acknowledge within 72 h.
2. security-engineer + regulatory-privacy-officer — approve scope (export / correction / deletion / consent withdrawal); check deadlines under Decree 356/2025.
2b. data-curator — if the user donated data (consent C3), exclude it from all future dataset versions and record lineage.
3. data-engineer — run `dsr_delete` or export flow across OLTP, S3, analytics, vector store, logs where applicable.
4. sre-operations — confirm backups policy (crypto-shredding or expiry) and record.
5. qc-release-gatekeeper — verify completion checklist; respond to user ≤ 30 days.

## PB-07 New third-party provider (LLM, OCR, email)
1. solution-architect — ADR with alternatives, exit strategy (adapter interface).
2. security-engineer — vendor assessment: data use/training, retention, region, certifications, DPA; cross-border transfer impact assessment (PDPL 91/2025 + Decree 356/2025).
2b. regulatory-privacy-officer — DPA terms, OTIA update if data leaves Vietnam, consent C2 text still accurate.
3. ai-ml-engineer (if AI) — eval on golden set; mlops-engineer — gateway allowlist, router config, fallback order, cost model.
4. cloud-devops-engineer — secrets, VPC endpoint/egress allowlist, budgets.
5. backend-engineer — adapter implementation + contract tests with mocks.

## PB-08 Security vulnerability report
1. security-engineer — triage CVSS, reproduce in staging, assign SLA (Critical 24 h, High 7 d, Medium 30 d, Low 90 d).
2. Owner skill — fix + regression test.
3. cloud-devops-engineer — patched release.
4. security-engineer — verify, close, thank reporter, update threat model.

## PB-09 Schema change touching analytics
1. backend-engineer — expand migration (add, don't drop).
2. data-engineer — update data contract version, dbt models, run backfill if needed.
3. qa-engineer — migration test + dbt tests.
4. backend-engineer — contract step (drop old column) only after consumers moved (≥ 1 release later).

## PB-10 Quarterly maintenance cycle
1. sre-operations — DR drill (restore RDS + S3 to temp account), record RTO/RPO achieved.
2. security-engineer — access review, tabletop exercise, threat model refresh.
3. ai-ml-engineer — re-evaluate newer models/providers.
4. cloud-devops-engineer — cost review, right-sizing, upgrade plan.
5. solution-architect — Well-Architected review, tech radar update.
6. product-manager — quarter OKR review, roadmap update.

## PB-11 Add a new input type (example: text-layer PDF, FHIR, patient text, CT)
| # | Owner | Deliverable | Gate |
| --- | --- | --- | --- |
| 1 | regulatory-privacy-officer | Does the input change the intended use? RDR note (CT → PB-16) | No contradiction with RDR |
| 2 | business-analyst | Stories + BR updates (BR-040…045 style) | DoR met |
| 3 | clinical-informaticist | Mapping/parsing spec (codes, FHIR, provenance) | Spec reviewed |
| 4 | security-engineer | Threat model delta (parsers, file types), SEC-AR-09 tests | No unmitigated High |
| 5 | ai-ml-engineer | Pipeline branch, new golden stratum, eval | Not worse than photo baseline on shared fields |
| 6 | backend-engineer | Intake API, PHI Service writes, `sourceType`, conflict handling | CI green, boundary tests green |
| 7 | clinical-safety-officer | Hazard-log delta, display review | No unacceptable residual risk |
| 8 | technical-writer / support-success | Help page, macros | Published VI/EN |
| 9 | qc-release-gatekeeper | Release checks | GO |

## PB-12 Acquire and onboard a dataset
| # | Owner | Deliverable | Gate |
| --- | --- | --- | --- |
| 1 | data-curator | Need statement (component, labels, size via sample_size.py, strata) | Approved by AI owner |
| 2 | data-curator | License Register row (training, product use, commercial, SA, DUA) | `license_register_check.py` PASS |
| 3 | regulatory-privacy-officer | Decision for NC/SA/DUA/unclear sources; DSA/ethics for partners | Decision recorded |
| 4 | data-curator | Download, checksum, Dataset Card, de-identification QA if needed | Card complete |
| 5 | data-curator | Leakage check vs golden set | `leakage_check.py` PASS |
| 6 | ai-ml-engineer | Use in eval/training; lineage to MC ids | G1-D before any training |

## PB-13 Reduce AI cost / change model routing
1. mlops-engineer — cost baseline from gateway logs; `cost_model.py` with real tokens and current prices.
2. ai-ml-engineer — shrink inputs (relevant pages, cleaned OCR), closed lists for mapping, compact schemas.
3. mlops-engineer — prompt caching, result cache, batch for non-urgent work; `threshold_tuner.py` on the dev set.
4. qa-engineer — eval gate: no Unit drops > 1 F1 point.
5. mlops-engineer — shadow → canary; watch USD/document, escalation ≤ 15%, latency; decision logged by product-manager.

## PB-14 Clinical safety case and gate G2-CS
1. clinical-safety-officer — hazard log complete for all features/inputs in the release (`hazard_risk_check.py` PASS).
2. qa-engineer — every CS requirement linked to passing tests (traceability matrix).
3. clinical-safety-officer — clinical validation (≥ 2 clinicians × ≥ 100 synthetic records), kappa and error analysis.
4. ux-ui-designer — summative usability with use-error scenarios.
5. clinical-safety-officer — Clinical Safety Case signed by a real clinician; residual risks justified.
6. qc-release-gatekeeper — record G2-CS; RG-15 evidence for the release gate.

## PB-15 Launch hypercare and gate G5-H
1. support-success — daily triage for 4 weeks, daily report, safety flags to the CSO within 1 working day.
2. sre-operations — SLO watch, error budget review, on-call.
3. owner skills — fast-track S1/S2 fixes via PB-05 light.
4. support-success — KB covers top-10 questions; `ticket_stats.py --g5h` PASS (no new S1/S2 in 14 days, no open safety items).
5. qc-release-gatekeeper — approve G5-H; product-manager — move the team to the next phase.

## PB-16 Feature near the regulatory boundary (example: CT in v2)
1. regulatory-privacy-officer — re-run G0-R: updated RDR with decision questions; expert advice if any answer is "yes"; claims list updated.
2. clinical-safety-officer — hazard analysis (e.g., CT illustration mistaken for a radiology read), display rules (watermark, no measurements).
3. security-engineer — threat model (DICOM parsers, large files, PHI in headers); SEC-AR-08/09.
4. data-curator — licensed public CT data only (License Register), G1-D before any fine-tuning.
5. medical-imaging-engineer — intake, de-ID, segmentation, mesh, registration (TRE < 15 mm), viewer without measurement tools.
6. mlops-engineer — GPU scale-to-zero serving, cost per case.
7. clinical-safety-officer — clinical validation of CT illustrations (e.g., 20 cases); qc-release-gatekeeper — release checks; release only within the RDR's scope.
