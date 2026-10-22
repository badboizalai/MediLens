# MediLens Test Strategy (v1)

Owner: `medilens-qa-engineer`. Binding sources: `RULES.md` C4, plan section 10.1, `docs/requirements/traceability.csv`. MediLens only illustrates and explains records (BR-042), so safety and copy checks are first-class tests.

## 1. Pyramid (target share of automated tests)
Unit ~65% - Integration/contract ~25% - E2E/visual ~10%. Non-functional suites sit beside it: performance, security/authz, accessibility, AI evaluation.

| App / area | Unit | Integration / contract | E2E / other | Tools already in repo |
| --- | --- | --- | --- | --- |
| `apps/api` | domain + application services | Testcontainers (Postgres, RLS), LocalStack, authz matrix per endpoint (`backend-engineer/assets/test-authz-template.py`), OpenAPI contract | k6 (`tests/load/smoke.js`) | pytest (`make test`), import-linter (`make api-lint`) |
| `apps/worker` | job handlers, retry/idempotency logic | Testcontainers + LocalStack SQS, outbox | - | pytest |
| `apps/web` | components, hooks, i18n | API client against mock server | Playwright (`tests/e2e`), axe | Vitest (`pnpm test`), Playwright, axe |
| `apps/ai-gateway` | redaction, routing, quota | provider stubs, no real network | prompt-injection cases | pytest |
| `apps/phi-service` | pseudonymisation, key handling | schema has no identity columns; API role cannot read PHI tables; DEK deletion | - | pytest, Testcontainers |
| `ml/` evaluation | metric functions | golden-set run (section 5) | red-team set | pytest, `ml/eval` |
| Governance | skill script tests | - | claims lint, hazard check, licence register, i18n check | `make governance` |

## 2. Risk-based focus
| Risk | Depth | Key suites |
| --- | --- | --- |
| PHI access control | Very high | authz matrix, RLS, IDOR abuse cases, audit assertions |
| AI extraction correctness | Very high | golden set, FDI/mapping unit tests, review-screen E2E |
| Medical safety wording | Very high | red-team set, guardrail tests, claims lint, one test per CS-xxx requirement |
| Sharing and expiry | High | decision tables with injected clock |
| Viewer correctness | High | visual baselines, `region_code` consistency check |
| Upload robustness | High | boundary/negative files, EICAR sample |
| Performance | Medium | k6 scenarios against NFRs |
| i18n | Medium | VI/EN key parity (`i18n_check.py`) |

## 3. Environments
| Env | Purpose | Data |
| --- | --- | --- |
| local | Docker Compose (`make up`) + LocalStack; unit, integration, E2E smoke | synthetic |
| CI | ephemeral containers per run; all blocking suites | synthetic |
| staging | prod-like; E2E, k6, UAT, exploratory | synthetic |
| prod | smoke and synthetic monitoring only | none created by QA |

## 4. Test data policy
Synthetic only. No real patient data in repo, fixtures, logs, prompts, dev or staging. `data/raw`, `ml/datasets/real`, `imaging/dicom-real` are gitignored. Fixtures come from the synthetic generators or hand-written records, are deterministic (seeded) and carry no real names, IDs or phone numbers. Test accounts are created per run and deleted after.

## 5. AI evaluation gates (plan section 10.1)
Fixed golden set (never used for tuning) plus a dev set. A run fails CI if any MVP threshold is missed or any Unit drops more than 1 F1 point against the registered baseline.

| Component | Metric | MVP gate | Target |
| --- | --- | --- | --- |
| Image quality check | precision/recall | >= 0.85 | >= 0.95 |
| Page classification | accuracy, macro-F1 | >= 0.85 | >= 0.95 |
| Printed OCR | CER | <= 5% | <= 2% |
| Handwritten OCR | CER | <= 20% | <= 10% |
| Field extraction | field F1 | >= 0.80 | >= 0.92 |
| ICD-10 normalisation | top-1 | >= 0.75 | >= 0.90 |
| Anatomical mapping | region accuracy | >= 0.85 | >= 0.95 |
| FDI tooth number | tooth accuracy | >= 0.90 | >= 0.98 |
| Confidence | ECE | <= 0.1 | <= 0.05 |
| RAG explanations | faithfulness | >= 0.85 | >= 0.95 |
| Hallucination | unsourced claims | <= 5% | <= 1% |
| Guardrails (100-question red-team) | block rate / false block | >= 95% / <= 10% | >= 99% / <= 5% |

## 6. Coverage targets (RULES C4)
>= 70% overall, >= 85% for `domain`. Coverage is a floor, not a goal. New behaviour starts with a failing test; a bug fix starts with a regression test.

## 7. Entry and exit criteria
Entry (story): acceptance criteria written, build on the test env, synthetic data ready.
Exit (release): all MUST tests pass; no open S1/S2; coverage floors met; AI gates pass; k6 within NFR; axe 0 serious/critical; security and authz suites pass; claims lint and hazard check green; test summary report written (QC gatekeeper runs the release gate).

## 8. Determinism and flaky-test policy
No real network, no real time (inject a clock), no shared state. A test that fails then passes on retry is flaky: label it within one working day, open a task id, then fix or quarantine (skip with the task id in the reason) within one sprint (RULES C4). Quarantined count is reported weekly; more than 2% quarantined blocks new E2E additions. CI retries: at most 1 for E2E, 0 for unit/integration.

## 9. Defect severity and priority
| Sev | Meaning |
| --- | --- |
| S1 | data exposure, data loss, main flow blocked for all |
| S2 | main flow broken for some users, no easy workaround, or wrong medical display |
| S3 | partial issue with workaround |
| S4 | cosmetic |

| Priority | Rule | Typical fix window |
| --- | --- | --- |
| P0 | stop work; S1, or any wrong medical display | same day |
| P1 | S2 | current sprint |
| P2 | S3 | next 2 sprints |
| P3 | S4 | backlog |

Priority can differ from severity (for example an S4 typo on the public disclaimer is P1). Any report that may harm a patient is routed to the Clinical Safety Officer.

## 10. Traceability
`docs/requirements/traceability.csv` maps BR to US to TC (`tc_level`, `status`). Every automated test carries its TC id in the name (for example `TC-101`). QA keeps `status` current. Release reports list each BR with no passing TC.
