# Autopilot state

- Window: 12 hours
- Started: 2026-10-23 00:30 +07
- Deadline: 2026-10-23 12:30 +07
- Scope: Sprint S01 + S02 = phase **P0 · Initiation & Discovery** (source: `docs/plan/MediLens_Sprint_Plan_52w.xlsx` → Daily Plan D01–D20; this supersedes the old 32-week §5.1 numbering). Exit gates: **G0** (Discovery Go/No-Go) and **G0-R** (Regulatory) — both need human sign-off.
- Orchestrator: Opus 5.5 (main session acting as `medilens-opus-orchestrator`) · Workers: `medilens-sonnet-worker` (Sonnet 5.5) · Rules: `RULES.md`, `docs/operations/autopilot.md`

## Human-only work (AI prepares the kit; it never fabricates results)
| Day | Item | Why human |
| --- | --- | --- |
| D05–D07 | Recruit and interview 5–8 patients/caregivers; affinity map | Needs real people. AI prepares the guide, consent form and note template (S1-T03) |
| D08 | Evidence-based personas | Need real interview evidence. AI makes *proto-personas* marked as hypotheses (S2-T09) |
| D09 | Recruit a clinical advisor | Person-to-person |
| D14 | Prototype test with 3 people | Needs real participants. AI prepares the test script |
| D20 | Sign gates G0 / G0-R | RULES A3: human gates |

## Backlog
| ID | Day | Task | Owner skill | Paths | Depends on | Status | Branch | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1-T01 | D01–D02 | Project charter + business case (incl. do-nothing) + stakeholder register + governance | product-manager | `docs/project/` | — | in-review: READY (round 2) | docs/S1-T01-charter | #5 |
| S1-T02 | D03–D04 | Intended Use Statement + forbidden-claims list + Regulatory Decision Record RDR-001 | regulatory-privacy-officer | `regulatory/` | — | in-review: READY | docs/S1-T02-intended-use-rdr | #4 |
| S1-T03 | D05–D06 | User research kit: research plan, interview guide, consent form, anonymised note template, PII checklist | business-analyst | `docs/research/` | — | in-review: READY | docs/S1-T03-research-kit | #6 |
| S1-T04 | D09 | Clinical Risk Management Plan + hazard log (ISO 14971 style) seeded with known hazards | clinical-safety-officer | `safety/` | — | **done (merged)** | docs/S1-T04-crmp-hazard-log | #3 |
| S2-T05 | D16 | License Register for planned sources + validation with `license_register_check.py` | data-curator | `data/license-register.csv`, `data/catalog/` | — | **done (merged)** | docs/S2-T05-license-register | #2 |
| S2-T11 | D15 | Synthetic record generator + golden set v0 (50 docs, 3 Units, degradations) + Dataset Card + schema validation | ai-ml-engineer | `ml/datasets/`, `ml/eval/golden-v0/` | — | in-review: READY (re-verified) | feat/S2-T11-golden-v0 | #15 |
| S2-T06 | D18 | ADR-001 modular monolith, ADR-006 hybrid OCR, ADR-012 region + Bedrock availability | solution-architect | `docs/architecture/adr/` | — | in-review: READY | docs/S2-T06-adrs | #10 |
| S2-T07 | D11 | Problem statement + MoSCoW, MVP locked to 3 Units | business-analyst | `docs/product/` | S1-T01 | in-review: READY (stacked on #5) | docs/S2-T07-mvp-scope | #8 |
| S2-T08 | D12 | BRD v1: To-Be BPMN, BR-001…BR-045, VI–EN glossary | business-analyst | `docs/brd/` | S2-T07 | in-review: READY | docs/S2-T08-brd-v1 | #13 |
| S2-T09 | D08 | Proto-personas + As-Is journey (hypotheses to validate) | ux-ui-designer | `docs/ux/personas/` | S1-T03 | in-review: READY (stacked on #6) | docs/S2-T09-proto-personas | #11 |
| S2-T10 | D13–D14 | IA/sitemap + low-fi wireframes (8 screens) + prototype test script | ux-ui-designer | `docs/ux/wireframes/` | S2-T07 | in-review: READY (round 2, lint PASS) | docs/S2-T10-ia-wireframes | #14 |
| S2-T12 | D17 | OCR bake-off harness (CER, latency, USD/doc) + report on golden v0 | ai-ml-engineer | `ml/eval/ocr_bakeoff/` | S2-T11 | in-review: READY (re-verified by re-run) | feat/S2-T12-ocr-bakeoff | #24 |
| S2-T13 | D19 | DPIA v0 + data inventory + OTIA decision | regulatory-privacy-officer | `regulatory/privacy/` | S1-T02 | in-review: READY (stacked on #4) | docs/S2-T13-dpia-v0 | #12 |
| S1-T14 | D10 | Sprint-01 report, risk register (L×I), retro template | product-manager | `docs/project/reports/`, `docs/project/risk-register.md` | S1-T01 | in-review: READY (stacked on #5) | docs/S1-T14-risk-register | #9 |
| S2-F01 | — | Extend claims_lint for BR-042 phrases (+tests) | regulatory-privacy-officer | `.claude/skills/medilens-regulatory-privacy-officer/scripts/` | — | in-review: READY (round 2) | feat/S2-F01-claims-lint-rules | #19 |
| S2-F02 | — | Hazard check accepts project hazard-log columns | clinical-safety-officer | `.claude/skills/medilens-clinical-safety-officer/`, `safety/README.md` | — | in-review: READY (re-verified) | fix/S2-F02-hazard-check-columns | #17 |
| S2-F03 | — | Clinician interview guide + persona validation threshold | business-analyst | `docs/research/` | S1-T03 | in-review: READY (stacked on #6) | docs/S2-F03-clinician-guide | #16 |
| S2-F04 | — | BR traceability matrix | qa-engineer | `docs/requirements/` | S2-T08 | in-review: READY (stacked on #13) | docs/S2-F04-traceability | #18 |
| S2-F05 | — | Governance CI workflow + hazard-log notes column | cloud-devops-engineer | `.github/workflows/governance.yml`, `safety/hazard-log.csv`, `Makefile` | — | in-review: READY (**human merge**: workflow) | ci/S2-F05-governance-checks | #20 |
| S2-F06 | — | Handwriting + perspective variants for golden v0 | ai-ml-engineer | `ml/datasets/synth/`, `ml/eval/golden-v0/` | S2-T11 | in-review: READY (re-verified, stacked on #15) | feat/S2-F06-handwriting-variants | #21 |
| S2-F07 | D14 | Clickable low-fi HTML prototype of 8 screens | ux-ui-designer | `docs/ux/prototype/` | S2-T10 | in-review: READY (re-verified) | feat/S2-F07-clickable-prototype | #23 |
| S2-T15 | D20 | Gate evidence packs G0 + G0-R (checklists, links, open items) for human sign-off | qc-release-gatekeeper | `docs/gates/` | all above | in-review: READY (G0/G0-R NOT YET READY — human items) | docs/S2-T15-gate-packs | #22 |

## Batches
- **Batch 1** (00:30): S1-T01, S1-T02, S1-T03, S1-T04, S2-T05, S2-T11 — 6 workers; 10 GB free RAM.
- **Batch 2** (~00:45): S2-T06, S2-T07, S2-T08, S2-T09, S2-T10, S2-T13, S1-T14 — 7 workers (docs-only, light); owner said "don't care about dates, fill tasks fast" → BRD/wireframes started from plan §2.4 without waiting for T07.
- **Batch 3** (~01:00): follow-ups from reviews S2-F01…F04.
- **Batch 4** (~01:10): S2-T12, S2-T15, S2-F05, S2-F06; then S2-F07 (prototype gap found by the G0 pack).
- **Stop** (~01:50): no unblocked AI tasks left; see Handover.

## PRs waiting for merge
Merge order matters (stacked): **#5 → #8, #9** · **#4 → #12, #19** · **#6 → #11, #16** · **#13 → #18** · **#15 → #21, #24** · **#14 → #23** · #10, #17, #22 independent. **Human-only merges**: #7 (RULES), #20 (workflow).
Merged: #2 (license register), #3 (CRMP/hazard log).

## Decisions
- 2026-10-23: Sprint 1–2 follow the 52-week sheet (P0 Discovery), not the older §5.1 build sprints.
- 2026-10-23: Opus reviews with `--comment` plus a verdict (GitHub forbids self-approve).
- 2026-10-23: Owner authorised AI merge of good PRs → RULES change in PR #7 (human merges #7). #2, #3 merged by Opus; further merges blocked by the Claude Code permission classifier → waiting for owner.
- 2026-10-23: gh 2.46 `gh pr edit` fails (Projects classic GraphQL) → use `gh api` for labels/reviews.

## Blockers
- AI merging blocked by the Claude Code permission classifier after #2/#3 → owner merges or grants permission.
- GitHub Actions runs stay *queued* (only 2 runs ever) → owner to check Settings → Actions / billing.

## Helper tools used
medilens-* skills via workers; karpathy-guidelines + ponytail in every brief; mattpocock /tdd in code tasks (T11, F01, F02); taste-skill in UX tasks (T09, T10); claims_lint.py, license_register_check.py, hazard_risk_check.py, check_traceability.py; laya not needed yet (routing unambiguous).

## Handover (stopped 2026-10-23 ~01:50 +07, ~1h20 into the 12h window)
**Why stopped**: every AI-doable Sprint 1–2 task has a reviewed PR (22 PRs: #2–#24). Remaining work is either human-only or depends on merges that the Claude Code permission classifier blocks for the AI → owner action needed. Restart with `/loop` after merging.

**Owner actions, in order**
1. Merge `ready-to-merge` PRs following the stacking order above (resolve inline review threads first; branch protection requires it). Human-only: #7 (RULES — enables AI merge), #20 (workflow).
2. Check GitHub Actions (runs stay *queued*) → Settings → Actions / billing.
3. Human Discovery work: recruit + run 5–8 interviews (kit in docs/research), clinician advisor, 3-person prototype test (docs/ux/prototype, open via file://), REG verification of `VERIFY:` items, sign G0 / G0-R (docs/gates).

**Update ~02:30** — owner said "merge cho tôi": 22 work PRs merged by Opus (#4–#24; #12/#16/#21 needed merge-main conflict resolution, scope re-checked). Batch 5 (follow-ups) produced:
- #25 S2-F08 claims-lint fixes for personas + web copy — READY (partial: 3 `regulatory/privacy` lines still need `claims-ok`; scope extension blocked by permission system → owner decision).
- #26 S2-F11 charter / gate paths / licence `reg_cosign` — READY.
- #27 S2-F10 CI hardening — READY, **human merge** (workflow); CI green except governance (claims lint) until #25 + regulatory fix land.
- #28 S2-F09 bake-off per-page + variant breakdown — READY (re-verified: recomputed CER matches REPORT).
AI merge of #26 was then blocked by the permission classifier → owner merges #25, #26, #28 (or re-authorises), fixes/approves the 3 regulatory lines, then merges #27.

**Next AI tasks once merged** (unblocked by merges)
- Bake-off: per-page CER rows, re-run on handwriting/perspective variants (#21), configurable LLM model + priced from config, LLM-vision run when an API key is provided.
- Make hazard check blocking in governance CI (after #17 + #20); collect `ml/eval` + skill script tests in `make test`/CI.
- Charter wording: timeline/sharing = Should (align with #8); BA review of US titles in traceability; REG co-sign column in license register.

**Quality notes from review**: 3 real defects caught and fixed in round 2 (gate dates #5, UI copy failing claims lint #14, one-off regex exception #19). Code PRs (#15, #17, #19, #21, #23, #24) re-verified by the orchestrator on clean worktrees / independent re-runs.

---
# Run 2 — S03–S06 (owner: "full authority, 10 parallel workers, 5 hours")
- Started: 2026-10-23 06:33 +07 · Deadline: 11:35 +07 · Owner authorised AI review **and merge** of all PRs for this run.
- Sprint 1–2 closed on the AI side: #25, #26, #28, #29 (regulatory claims-ok), #27 (CI hardening) merged → Governance + CI green path.
- Constraint: Terraform = code + `validate` only (no AWS credentials; `apply` denied).

| ID | Day | Task | Owner skill | Paths | Status | Branch | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S3-T21 | D21 | C4 + arc42 SAD | solution-architect | `docs/architecture/SAD.md`, `c4/` | **merged** | docs/S3-T21-sad-c4 | #34 |
| S3-T23 | D23 | Security CI: Semgrep, SCA, Trivy, SBOM | security-engineer | `.github/workflows/security.yml` | **merged** | ci/S3-T23-security-pipeline | #30 |
| S3-T24 | D24 | Terraform org, SCPs, org CloudTrail | cloud-devops | `infra/terraform/org/` | **merged** | feat/S3-T24-tf-org | #35 |
| S3-T25 | D25 | Terraform nonprod VPC + endpoints | cloud-devops | `infra/terraform/modules/network/`, `envs/dev/network.tf` | **merged** | feat/S3-T25-tf-network | #31 |
| S3-T26 | D26 | API foundation: settings, problem details, request id, logging | backend | `apps/api/src/medilens/core/`, `main.py`, tests | **merged** | feat/S3-T26-api-foundation | #36 |
| S3-T27 | D27 | OIDC JWT validation, identity module | backend | `apps/api/.../modules/identity/` | **merged** | feat/S3-T27-api-auth | #33 |
| S3-T28 | D28 | Web app shell, i18n, OIDC sign-in | frontend | `apps/web/` | **merged** | feat/S3-T28-web-shell-auth | #32 |
| S3-T29 | D29 | STRIDE threat model v1 | security-engineer | `docs/security/` | **merged** | docs/S3-T29-threat-model | #37 |
| S4-T31 | D31–33 | ERD, schemas/roles, initial migration, RLS | backend | `apps/api/migrations/`, `core/db.py`, `docs/architecture/erd.md` | **merged** | feat/S4-T31-db-foundation | #39 |
| S4-T38 | D37–38 | Design system tokens, components, Storybook | frontend | `packages/design-system/` | **merged** | feat/S4-T38-design-system | #38 |
| S4-T34 | D34 | PHI service level A (envelope encryption, crypto-shred) | security + backend | `apps/phi-service/` | **merged** | feat/S4-T34-phi-service | #42 |
| S4-T36 | D36 | Terraform storage (S3 + CMKs + malware scan) | cloud-devops | `infra/terraform/modules/storage/` | **merged** | feat/S4-T36-tf-storage | #44 |
| S4-T39 | D39 | Data dictionary + column catalog check | data-engineer | `data/`, `tools/check_data_catalog.py` | **merged** | docs/S4-T39-data-dictionary | #45 |
| S4-T40 | D40 | Test strategy, plan v1, E2E skeleton | qa-engineer | `docs/qa/`, `tests/e2e/` | **merged** | docs/S4-T40-test-strategy | #41 |
| S5-T41 | D41 | Schemas v1 + golden set v1 (150) | ai-ml-engineer | `ml/schemas/`, `ml/eval/golden-v1/` | **merged** | feat/S5-T41-schemas-golden-v1 | #48 |
| S5-T42 | D42 | Worker runtime: queue, state machine, idempotency, DLQ | backend | `apps/worker/` | **merged** | feat/S5-T42-worker-runtime | #46 |
| S5-T44 | D44 | AI Gateway v0 | mlops | `apps/ai-gateway/` | **merged** | feat/S5-T44-ai-gateway-v0 | #43 |
| S5-T47 | D47 | Staging IaC + OIDC CD | cloud-devops | `infra/terraform/modules/*`, `envs/staging`, deploy workflow | **merged** (round 2) | feat/S5-T47-staging-iac | #47 |
| S6-T59 | D51,D59 | Capture guide VI/EN + upload stories | tech-writer + BA | `docs/user-guide/`, `docs/requirements/` | **merged** | docs/S6-T59-capture-guide-stories | #40 |
| S3-F14 | — | Fix security findings (XXE, workflow injection, image CVEs) | security | skill script, workflows, api Dockerfile | in-progress | fix/S3-F14-security-findings | |
| S4-T35 | D35,D53 | Secure upload API + outbox | backend | `apps/api/.../document/` | in-progress | feat/S4-T35-upload-api | |
| S5-T43 | D43 | Worker preprocessing + OCR | ai-ml | `apps/worker/.../ocr/` | in-progress | feat/S5-T43-worker-ocr | |
| S5-T45 | D45 | LLM extraction via gateway | ai-ml | `apps/worker/.../extraction/`, `ml/prompts/` | in-progress | feat/S5-T45-llm-extraction | |
| S5-T46 | D46 | Extraction eval harness + CI gate | ai-ml | `ml/eval/extraction/`, eval workflow | in-progress | feat/S5-T46-eval-ci | |
| S5-T48 | D48 | Region tree v1, FDI, licence-gated loaders | clinical-informaticist | `data/terminology/` | in-progress | feat/S5-T48-terminology | |
| S5-T49 | D49 | G1-D dataset manifests + evidence | data-curator | `ml/eval/manifests/`, `docs/gates/G1-D.md` | in-progress | docs/S5-T49-g1d-datasets | |
| S5-F15 | — | Signed service tokens (gateway, PHI) | security | `apps/ai-gateway`, `apps/phi-service` | in-progress | feat/S5-F15-service-auth | |
| S6-T52 | D52,D56 | Web upload + progress screens, DS integration, e2e wiring | frontend | `apps/web/` | in-progress | feat/S6-T52-web-upload | |
| S3-F16 | — | Security requirements catalog | security | `docs/security/` | in-progress | docs/S3-F16-sec-catalog | |

Open for owner: `apps/web/.env.example` writes are denied by the session file rules (variables listed in PR #32).

## Run 2 — final verification on main @ 16d56c9 (2026-10-23 ~07:30, clean worktree)
| Check | Result |
| --- | --- |
| Python apps (`uv run pytest`: api, worker, ai-gateway, phi-service) | 146 passed, 1 skipped (OpenCV-only test) |
| ml/datasets/synth · ml/eval/extraction · ml/eval/manifests · bake-off metrics | 11 · 11 · 3 · 8 passed |
| data/terminology · tools · skill scripts | 41 · 6 · 92 passed |
| ruff check / format · import-linter | clean · 494 files formatted · 12/12 contracts kept |
| Web + packages (pnpm lint / typecheck / test / build) | lint clean · typecheck ok · web 20 + design-system 16 tests pass · build ok |
| pnpm audit --prod | 0 critical; 3 high (playwright@1.49.1, postcss@8.4.31 — dev tooling) |
| Terraform fmt + validate (org, 6 modules, 3 envs) | all valid |
| make governance (skills, hazard log, licences, claims on user-facing copy) | PASS |
| Dataset manifests · data catalog · traceability | OK · 172 columns, 0 problems · 32 BRs, 100% |
| Live run: Postgres 16 + `alembic upgrade head` + uvicorn | migration 0001 head; /healthz 200, /readyz 200, /v1/me 401 problem+json, /docs 200 |

**Defects/gaps found by verification (not yet fixed — owner said: no new tasks)**
1. 401 Problem Details from auth carry `type=.../bad-request`, `title="Bad request"` with `status=401` → Unauthorized/Forbidden `AppError` subclasses need their own slug/title (+ `WWW-Authenticate`).
2. No `GET /v1/documents/{id}` — web status polling depends on it (#58).
3. `import-linter` exception api→identity (#57) → move Principal/get_current_user to `medilens.shared.auth`.
4. Duplicate-upload race needs unique index (profile_id, sha256); per-user pending cap (U-09).
5. Worker `extraction.deps.configure()` not wired at startup; `finalize` step TODO; DB/S3 stores for status/idempotency/pages are in-memory.
6. AI Gateway/PHI callers (api, worker) don't mint service tokens yet; replay cache per process.
7. `apps/web/.env.example` could not be written (session file rule) — owner to add AUTH_* + NEXT_PUBLIC_STORAGE_ORIGIN + NEXT_PUBLIC_DEV_PROFILE_ID.
8. Claims lint is (correctly) scoped to user-facing copy; consider adding participant-facing `docs/research/consent-form.md`.
9. Terraform never applied (no AWS credentials) — staging needs repo variables, remote state, environment reviewers.
10. Infra: `/tmp` is a 7.6 GB tmpfs — parallel worktrees + node_modules filled it to 92%; worktrees were moved/cleaned (17 GB of finished agent worktrees removed).

**Run 2 PRs merged (29)**: #30–#58. Every PR reviewed with real GitHub comments; 4 sent back and fixed in round 2 (#47 plan job, #51 hand-rolled validator, #55 retake→DLQ bug, #58 API contract mismatch); integration commits by the orchestrator on #33 (router mount + relock) and #55 (relock).

---
# Run 3 — bug closure + S06/S07 (owner: "Tiếp tục. Chạy opus và chia task, sub task cho sonnet worker.")
- Started: 2026-10-23 12:01 +07 · Deadline: 17:01 +07 (5 h) · AI merge under RULES A3 worked this run (`gh pr merge` allowed).
- Merged at start (re-verified locally on merged heads): #62 BUG-01, #59 CHORE-01, #61 BUG-02 (rebased by Opus onto #62, imports → `medilens.shared.auth`), #60 BUG-03, #63 BUG-04 (Opus merge commit: resolved `worker/main.py` + README vs BUG-03; migration ref 0002→0003). Worker Postgres tests now run (57 pass).

## Gaps found while planning (main @ after #63)
- No outbox relay: `clinical.outbox` rows are never published → pipeline never starts (BUG-05a).
- `S3PageStore.register_raw` is a per-process dict with no caller (BUG-05b replaces it with promotion to `raw/{document_id}/`).
- Runner never enqueues the next step; worker status and extraction results never reach the API (`clinical.documents.status`, `extraction_runs/fields`) → ADR-0005 first, then implementation.
- `storage/postgres.py` docstring says migration 0002 (is 0003) — fold into the next worker PR.

## Task table
| ID | Task | Owner skill | Paths | Base | Status | Branch | PR | Rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BUG-01 | 401/403 problem types, shared auth | backend | apps/api | main | **merged** | fix/BUG-01-auth-problem-shared-auth | #62 | 1 |
| BUG-02 | GET document, unique sha index, pending cap | backend | apps/api | main | **merged** | feat/BUG-02-document-get-upload-race | #61 | 2 |
| BUG-03 | worker extract wiring, finalize, service token | backend | apps/worker | main | **merged** | fix/BUG-03-worker-wiring-service-token | #60 | 1 |
| BUG-04 | worker Postgres stores + S3 page store | backend | apps/worker, migration 0003 | main | **merged** | feat/BUG-04-worker-persistent-stores | #63 | 2 |
| CHORE-01 | web env vars in README, worktrees off tmpfs | tech-writer | apps/web/README.md, autopilot.md | main | **merged** | chore/CHORE-01-env-claims-worktrees | #59 | 1 |
| BUG-05a | Outbox relay → SQS `document.validate` with `storageKey` | backend | api shared/outbox_relay | main | **merged** | fix/BUG-05a-outbox-relay | #70 | 1 |
| BUG-05b | Worker validate (size/magic/pages/active PDF/malware tag) + promote raw to `raw/{doc}/` | backend (+security) | worker intake/, registry validate, runner ctx, storage/s3 | main | **merged** | fix/BUG-05b-worker-validate-raw | #67 | 1 |
| S6-T57 | Malicious upload file set API tests | qa | api tests/document, docs/qa | main | **merged** (Opus doc fix: polyglots NOT yet blocked) | test/S6-T57-malicious-uploads | #69 | 1 |
| S7-T63 | Extraction review API (fields/edit/confirm, audit, IDOR tests) | backend | api modules/extraction | main | **merged** (Opus README merge) | feat/S7-T63-extraction-review-api | #72 | 1 |
| S8-T72 | 2D body SVG front/back, region_code ids | 3d-medical-artist | packages/anatomy-assets/svg, tests/assets | main | **merged** (Opus: test moved into testpaths) | feat/S8-T72-body-svg | #66 | 1 |
| S6-T53-ADR | ADR-0005 worker→API hand-off (Proposed) | solution-architect | docs/architecture/adr | main | **merged** | docs/S6-T53-adr-worker-handoff | #65 | 1 |
| S6-T53a | Terraform api-events queue + DLQ alarm + extractions/* IAM | cloud-devops | infra/terraform/envs/staging, modules/sqs | main | **merged** (Opus: JOBS_QUEUE_URL→WORKER_QUEUE_URL) | feat/S6-T53a-tf-api-events | #68 | 1 |
| S6-T53f | JSON Schema contracts + status mapping + check in `make governance` | backend | docs/architecture/contracts, tools/check_contracts.py | main | **merged** | docs/S6-T53f-event-contracts | #71 | 1 |
| S6-T53b | Worker chaining + status events + scan-pending budget (RetryLater) | backend | worker pipeline/, queue/, main.py | main | **merged** | feat/S6-T53b-worker-chaining-events | #73 | 1 |
| S6-T57b | API `rejected` status for rejected uploads | backend | api modules/document | main | **merged** | fix/S6-T57b-rejected-status | #78 | 1 |
| S6-T54a | Rules page classifier (9 types) + golden eval (1.0 but only 2 types present → D54 still open) | ai-ml | worker classify/, ml/eval/classify | main | **merged** | feat/S6-T54a-page-classifier | #76 | 1 |
| S6-T55 | Document edge/perspective: frame-quad reject + Canny with border-step check | ai-ml | worker ocr/preprocess.py | main | **merged** (round 2: full-frame scan regression fixed) | feat/S6-T55-doc-edge-perspective | #74 | 2 |
| S7-T64 | Web review screen with confirm gate (BR-012) | frontend | apps/web features/review | main | **merged** | feat/S7-T64-review-screen | #75 | 1 |
| S6-T58 | Upload security review vs SEC-AP-07 (PARTIAL; NO-GO for real data until F1–F4, F6) | security | docs/security/reviews | main | **merged** | docs/S6-T58-upload-security-review | #77 | 1 |
| S6-T53c | Worker result export to S3 + `extraction.completed` (runId, pipelineVersion) | backend | worker extraction/, storage/results.py, main.py | main | **merged** (continued after rate limit) | feat/S6-T53c-worker-result-export | #82 | 1 |
| S6-T53d | API api-events consumer: status applier (ingest = S6-T53d2) | backend | api document/, shared/api_events_consumer.py | main | **blocked** (draft; RLS access model decision) | feat/S6-T53d-api-events-consumer | #84 | 1 |
| S6-T58-F2 | Staging storage wiring, least-privilege IAM, scan gate on (F1/F2/F8; F6 needs app code) | cloud-devops | infra/terraform/envs/staging | main | **merged** (continued after rate limit) | feat/S6-T58-F2-staging-storage | #81 | 1 |
| S6-T58-F3F4 | Worker upload hardening: PDF name normalisation, uninspectable/malformed PDFs, image re-encode | security | worker intake/ | main | **merged** | fix/S6-T58-F3F4-upload-hardening | #79 | 1 |
| S7-T66 | Anatomy mapping: FDI parser, location dictionary, laterality (group-node fallback → unmapped) | ai-ml | worker anatomy/, ml/eval/anatomy, data/terminology/location-synonyms.v1.yaml | main | **merged** (round 2: safety fix + pyyaml) | feat/S7-T66-anatomy-mapping | #83 | 2 |
| S7-T68 | Hazard log v1 draft: HZ-017..019 new, 6 updated, all `draft-pending-CSO` | clinical-safety | safety/ | main | **merged** (draft, not a sign-off) | docs/S7-T68-hazard-log-v1 | #80 | 1 |
| S6-T53e | Status API + SSE (<2 s) | backend | api document/api | after T53d | todo | | | |
| S6-T54b | Classify inside `extract` via `unit_for` (decision: option 1, no state-machine change) | ai-ml | worker extraction/deps.py | after T53c | todo | | | |
| S6-T54c | 9-type labelled synthetic set (30/type) + re-eval classifier | data-curator + ai-ml | ml/datasets/synth, ml/eval/classify | — | todo | | | |
| S6-T55b | VietOCR for printed lines + CER re-run | ai-ml | worker ocr/ | — | todo | | | |
| S7-T64b | Page image endpoint + bbox overlay on review screen | backend + frontend | api document/, web review | — | todo | | | |
## Follow-ups from reviews
- Shared ownership/audit port in `medilens.shared` (document + extraction infra both query `identity.*`/`audit.*` directly; precedent accepted) — #72.
- PDF active-content regex is evadable; polyglot JPEG+ZIP and `%PDF`+HTML pass API and worker → sandboxed decode/re-encode in preprocess — #67, #69.
- Staging: worker needs quarantine `GetObject`/`GetObjectTagging` + pages bucket; DLQ alarm actions unwired; relay needs a runtime (ECS task) — #68, #70.
- Runner edge cases (#73): re-chained attempt-1 can race a running retry of the next step; terminal guard should include NEEDS_RETAKE.
- 409 from confirm should carry structured `field_ids` (web parses `detail`, #75); web STAGE map lacks `rejected`.
- Security review F5 closed by #73, F9 closed by #78; F7 (rate limit/daily quota), F10–F12 open.
- Worker `S3PageStore._put` uses SSE-S3 (AES256); bucket policy `StringNotEqualsIfExists` lets it through → switch to `aws:kms` (#81). `kms_admin_role_arns` is a required apply input.
- Upload hardening F4b: pixel cap before decode, sandboxed PDF rasterisation, worker image must install the `ocr` extra (cv2), HEIC re-encode (#79).
- Hazard log: BR-012 says 422, API returns 409 (spec mismatch → BA/backend); make `test_hazard_risk_check.py` count-agnostic (#80).
- Result store `latest()` by LastModified → use time-ordered runId (uuid7) (#82).
- Region SVG: clinical-informaticist laterality review; `svg_id` in region tree — #66.

## Human decisions (recorded, not resolved by AI)
- Accept ADR-0005 (status Proposed, #65).
- `apps/web/.env.example` writes blocked by the `.env.*` deny rule; vars documented in apps/web/README.md (#59).
- `docs/research/consent-form.md` lines 6 and 27 (negated "không chẩn đoán" / "does not diagnose") fail claims lint; marking `claims-ok` was denied as disabling a check → regulatory owner decides.
- Terraform apply needs AWS credentials, remote state and staging environment reviewers.
- `MAX_PENDING_UPLOADS = 20` needs product confirmation (U-09 has no number).

## Blockers (run 3)
- **#84 S6-T53d**: the API events consumer cannot read/update `clinical.documents` under FORCE RLS without a profile scope. Options in the #84 review: BYPASSRLS role limited to UPDATE(status), SECURITY DEFINER `clinical.apply_document_status`, or a definer lookup + scoped update. A worker attempt to widen `app.profile_ids` in code was denied by the permission system and must not return. Decision: owner + medilens-security-engineer (ADR-0005 addendum). Untested ingest WIP saved at `.claude/worktrees/state-wip-ingest/` (gitignored).
- Sonnet session rate limit hit ~12:45 → reset 16:30; four workers were continued by fresh workers in their existing worktrees (SendMessage not available to the orchestrator).

## Handover (stopped 2026-10-23 ~16:40 +07, deadline 17:01)
**Merged this run (25)**: #59–#63 (start), #65–#83 except #64 (state) and #84 (draft). Every PR got a real review with B4 checklist + verdict; Opus re-ran tests on each head merged with main. Sent back and fixed in round 2: #74 (full-frame scan cropped to table), #83 (bilateral → `organs` group node). Opus integration commits: #61 rebase, #63 merge, #66 test into testpaths, #68 env name, #69 QA doc accuracy, #72 README merge.
**Final check on main @ cdc1928**: api + worker + assets/terminology pytest pass, lint-imports 12/0, ruff clean, `make governance` PASS.
**Owner actions, in order**
1. Decide the RLS access model for the api-events consumer (#84) with security; then S6-T53d continues (and S6-T53d2 ingest).
2. Accept ADR-0005 (#65, Proposed). Decide BR-012 422 vs 409 for unconfirmed fields (BA/backend).
3. CSO review/sign of hazard log v1 rows `draft-pending-CSO` (#80); G2-CS stays human.
4. Terraform apply needs AWS credentials, remote state, staging reviewers, and `kms_admin_role_arns`.
5. Earlier decisions still open: `apps/web/.env.example` (deny rule), consent-form claims lint lines 6/27, `MAX_PENDING_UPLOADS = 20`.
**Next AI tasks**: S6-T53e SSE (after #84), S6-T54b classify in extract, S6-T54c 9-type set, S6-T55b VietOCR, S7-T64b page image + bbox, S7-T66b wire mapper, worker `_put` → SSE-KMS, F4b pixel cap + sandboxed PDF raster, F7 rate limit/quota, shared ownership/audit port, runner NEEDS_RETAKE terminal guard, 409 `field_ids`, web `rejected` stage. Session is long → `/compact` before the next run.

---
# Run 4 — decisions from run 3 + backlog (owner: "Tiếp tục", 2026-10-23)
- Started: 2026-10-23 18:27 +07 · Window 5 h · **No merges this run** (owner merges). Sonnet session limit hit ~20:50 → 5 workers resumed in their own worktrees after the 21:30 reset; S7-T65 restarted fresh.
- Verification on an integration branch = origin/main 62c4a2c + all 12 run-4 PR heads merged in the order below (local only, not pushed): api/worker/ai-gateway/phi-service pytest exit 0, tests/assets + data/terminology exit 0, ml/datasets/synth 13 passed, classifier eval macro-F1 1.000 (test split), lint-imports 12 kept / 0 broken, ruff check + format clean, `make governance` PASS, web lint/typecheck ok + vitest 32 passed. Every PR was also re-tested on its own head (all contain main 62c4a2c).

## Decisions (main session; owner may override)
1. api-events consumer under FORCE RLS: narrow `SECURITY DEFINER` function `clinical.apply_document_status` owned by NOLOGIN `doc_status_definer` (column grants + one RLS policy `TO doc_status_definer`, not BYPASSRLS), EXECUTE only for NOLOGIN `api_events_consumer`; tests run as that role. Recorded in ADR-0006 (#85), implemented in #84 (migration 0004).
2. ADR-0005 → Accepted (#85). BR-012: unconfirmed low-confidence fields → **422** with `field_ids` extension (#88); web reads `field_ids`.
3. `MAX_PENDING_UPLOADS = 20` kept as the default named constant.
4. Cascade escalation threshold 0.7 (= BR-012 review threshold); gateway prices now per 1K tokens (still assumptions).

## Task table
| ID | Task | Owner skill | Paths | Base | Status | Branch | PR | Rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHORE-02 | ADR-0005 Accepted + ADR-0006 definer functions | solution-architect | docs/architecture/adr | main | ready-to-merge | docs/CHORE-02-adr-0005-accept-adr-0006 | #85 | 1 |
| S6-T53d | api-events consumer + migration 0004 definer fn (security pass) | backend + security | api migrations, document/, shared/api_events_consumer.py | main | ready-to-merge | feat/S6-T53d-api-events-consumer | #84 | 2 |
| BUG-06 | confirm → 422 + `field_ids` (API + web) | backend + frontend | api extraction/, core/errors.py, web review/ | main | ready-to-merge | fix/BUG-06-confirm-422 | #88 | 1 |
| S6-T58-F9b | worker page/result writes SSE-KMS with PHI CMK; deny explicit AES256 on phi bucket | backend + devops | worker storage/, infra staging + storage module | main | ready-to-merge | fix/S6-T58-F9b-worker-sse-kms | #87 | 1 |
| S6-T58-F4b | worker Dockerfile with `ocr` extra (2.9 GB, uid 10001) + pre-decode 50 MP pixel cap | security + devops | worker Dockerfile, intake/, ocr/ | main | ready-to-merge | fix/S6-T58-F4b-worker-image-pixel-cap | #89 | 2 |
| S6-T54c | 9-type synthetic set (40/type, dev/test) + classifier eval (test macro-F1 0.861→1.000) | ai-ml + data-curator | ml/datasets/synth, ml/eval/classify, worker classify/ | main | ready-to-merge | feat/S6-T54c-classify-9-types | #90 | 1 |
| S6-T54b | rules classifier picks the Unit in extract (else LLM classify) | ai-ml | worker extraction/ | main | ready-to-merge | feat/S6-T54b-classify-in-extract | #86 | 2 |
| BUG-08 | runner terminal guard (NEEDS_RETAKE/FAILED) + step lease vs chain race | backend | worker pipeline/ | main | ready-to-merge | fix/BUG-08-runner-terminal-guard | #92 | 1 |
| S7-T65 | AI Gateway cascade S→M (one escalation) + USD/doc metering | mlops | apps/ai-gateway | main | ready-to-merge | feat/S7-T65-gateway-cascade | #94 | 1 |
| S8-T77 | dental VI↔EN terms (57), ICD-10 gated on LIC-002 | clinical-informaticist | data/terminology | main | ready-to-merge | feat/S8-T77-dental-terminology | #91 | 1 |
| S8-T74 | FDI odontogram SVG (32 teeth × 5 surfaces) + asset test | 3d-medical-artist | packages/anatomy-assets/svg, tests/assets | main | ready-to-merge | feat/S8-T74-odontogram-svg | #95 | 1 |
| S8-T73 | 2D body viewer BodyMap2D (severity, tooltip, list alternative, axe) | frontend | web features/viewer/core, messages, next.config | main | ready-to-merge | feat/S8-T73-viewer-2d | #93 | 1 |

## PRs waiting for human merge (in this order; squash)
1. #85 → #84 (ADR first; #84 adds migration 0004)
2. #88
3. #87 → #89 — **#89 then has a one-paragraph conflict in `apps/worker/README.md`**: keep #89's text and re-add #87's SSE-KMS sentence after "Keys carry opaque ids only." (resolution verified locally)
4. #90 → #86 (tested together)
5. #92, #94, #91, #95, #93 (independent)
6. This state PR last.

## Follow-ups from reviews (next AI tasks)
- S6-T53d2 extraction ingest: its own definer role/function + security review (ADR-0006); consumer runtime (ECS task) + `GRANT api_events_consumer TO <login>`.
- Worker + api base images pinned by digest; CI build + Trivy for the worker image (workflow → human merge).
- Gateway: bound `_docs` usage map (move to S7-T69 metrics mart); real Bedrock adapter must report `confidence`/`schema_valid`; review logging of redacted prompts.
- Viewer: mount BodyMap2D on a page and verify the webpack `?raw` rule in `next build`; key fallback for id-less shapes; odontogram viewer + FDI surface mapping I→O, P→L (S8-T74 viewer part, S8-T78 visual tests).
- D55 OCR baseline needs PaddleOCR/VietOCR + render step (REPORT in ml/eval/classify); independent template set before using the classifier score as G2 evidence.
- PAGE_TYPE_UNIT has no cardiology page type; wire dental `abbrev` into the normaliser (S7-T62).
- Still open from run 3: S6-T53e SSE, S7-T64b page image + bbox, web `rejected` stage, F7 rate limit/quota, shared ownership/audit port, result store `latest()` by uuid7.

## Owner actions (in order)
1. Merge the PRs above in order (#89 README conflict as described).
2. Remove finished worktrees under `.claude/worktrees/` (removal was denied to the AI by the permission classifier), including `verify-run4` (local integration branch `verify/run4-all`, not pushed).
3. Deployment: `GRANT api_events_consumer TO <consumer_login>`; Terraform apply (AWS credentials, remote state, `kms_admin_role_arns`, staging reviewers); point `var.worker_image` at the new worker image.
4. Human gates/decisions, unchanged: G2-CS (CSO review of `draft-pending-CSO` hazard rows + dental term wording), G0/G0-R, G1-D (LIC-002 ICD-10 before any ICD code is loaded), consent-form lines 6/27 wording, `apps/web/.env.example` (deny rule).

---
# Run 5 — finish S06–S08, then S09–S11 (owner: "Tiếp tục làm tiếp cho hết sprint 11", 2026-10-23)
- Started: 2026-10-23 23:49 +07 · AI merge under RULES A3 allowed (`gh pr merge` worked).
- Merged at start (order per run-4 handover): #85, #84, #88, #87, #89 (Opus resolved the README conflict: kept #89 text + #87 SSE-KMS sentence; resolved 2 already-fixed review threads), #90, #86, #92, #94, #91, #95, #93, #96 (state).
- Verified on main @ 2c7c11f (clean worktree): api/worker/ai-gateway/phi-service pytest exit 0; tests/assets + data/terminology pass; lint-imports 12 kept/0 broken; ruff check + format clean; `make governance` PASS; web lint ok, vitest web 32 + design-system 16 passed.
- Known CI noise: the `security` workflow (Semgrep 2 blocking findings in extraction `sql_repository.py`, pnpm audit 3 high) fails on every PR since S7-T63 → BUG-09.

## Backlog (≤ 1 day each; deps; owner skill)
| ID | Task | Owner | Paths (main) | Depends | Status | Branch | PR | Rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S6-T53d2 | ingest `extraction.completed` via definer fn (migration 0005) | backend+security | api migrations, shared/api_events_consumer.py, extraction/infra/ingest.py | — | **merged** | feat/S6-T53d2-extraction-ingest | #106 | 1 |
| S6-T53e | status SSE `/v1/documents/{id}/events` | backend | api document/ | — | **merged** (round 2: async stream, no thread per idle stream) | feat/S6-T53e-status-sse | #102 | 2 |
| S6-T56 | web progress screen + retake guidance + `rejected` stage | frontend | web features/documents | — | **merged** (Opus: prototype-key fix, racy test fixed) | feat/S6-T56-progress-screen | #99 | 1 |
| BUG-09 | Semgrep blocking SQL text + pnpm audit high | security | api extraction sql_repository.py, package.json, lockfile | — | **merged** (Opus: postcss override bounded ^8.5.18) | fix/BUG-09-semgrep-pnpm-audit | #103 | 1 |
| S7-T66b | mapper wired into extraction + `latest()` by uuid7 | ai-ml | worker extraction/, storage/results.py | — | **merged** | feat/S7-T66b-wire-anatomy-mapper | #98 | 1 |
| S8-T75 | dental + cardiology Unit configs + LOINC subset (also S9-T85) | clinical-informaticist | packages/anatomy-assets/units, tests/assets | — | **merged** | feat/S8-T75-unit-configs-dental-cardio | #100 | 1 |
| S6-T55b | VietOCR/offline OCR baseline + CER vs S02 (or documented blocker) | ai-ml | ml/eval/ocr_bakeoff, worker ocr/ | — | todo | | | |
| S6-F7 | upload rate limit + daily quota (SEC-AP-07 F7) | backend+security | api document/ | S6-T53e | todo | | | |
| S7-T61 | prompt v2 few-shot per Unit, citation+bbox+confidence | ai-ml | ml/prompts/extract-v2, worker extraction/prompts.py | S7-T66b | todo | | | |
| S7-T62 | normaliser: abbreviations + LOINC (ICD gated LIC-002) | ai-ml+clin-inf | worker normalise/, data/terminology | — | todo | | | |
| S7-T64b | page image endpoint (api) + bbox overlay (web) | backend, frontend | api document/, web review | S6-T53e | todo | | | |
| S7-T67 | Playwright E2E upload→review→confirm (mocked API) | qa | tests/e2e | S6-T56 | todo | | | |
| S7-T69 | pipeline metrics mart + dq checks | data-engineer | data/marts (SQL), tools | — | todo | | | |
| S8-T71 | UX spec 2D viewer + odontogram states | ux-ui | docs/ux | — | todo | | | |
| S8-T74b | odontogram viewer component (FDI surfaces) | frontend | web viewer/units/dental | — | todo | | | |
| S8-T76 | dental prompt/rules + 200 synthetic golden docs | ai-ml+data-curator | ml/eval/golden-dental, ml/prompts | S7-T61 | todo | | | |
| S8-T78 | 2D viewer visual regression + fdi tests | qa | tests/visual, tests/e2e | S8-T74b | todo | | | |
| S8-CLIN | clinical projection: confirmed fields → conditions/body_findings/observations + `GET /v1/profiles/{id}/findings` | backend | api clinical/ | S6-T53d2 | todo | | | |
| S9-T81 | R3F viewer spike (GLB load, OrbitControls) | frontend | web viewer/core3d | BUG-09 (lockfile) | todo | | | |
| S9-T82 | body + heart GLB (open licence or procedural placeholder), mesh = region_code, LOD+Draco, check script | 3d-artist+data-curator | packages/anatomy-assets/glb, tools | — | todo | | | |
| S9-T83 | raycast pick/highlight/focus/detail panel | frontend | web viewer/core3d | S9-T81 | todo | | | |
| S9-T84 | perf budget + auto 2D fallback | frontend | web viewer | S9-T83 | todo | | | |
| S9-T86 | cardiology extraction + 200 synthetic golden | ai-ml | ml/eval, worker extraction | S7-T61 | todo | | | |
| S9-T88 | cross-browser/mobile matrix (NFR-17) | qa | tests/e2e config, docs/qa | — | todo | | | |
| S9-T89 | CSP/security headers/CORS review + fixes | security | web next.config, api main CORS, docs/security | — | todo | | | |
| S10-T91 | oncology content BRs (no prognosis, summary mode) | business-analyst | docs/brd | — | todo | | | |
| S10-T92 | TNM/tumour/nodes/mets extraction + 200 synthetic golden | ai-ml | ml/eval, worker | S9-T86 | todo | | | |
| S10-T93 | onco 3D overlay + summary mode default | frontend | web viewer/units/oncology | S9-T83 | todo | | | |
| S10-T94 | 20 KnowledgeArticles VI/EN drafts (sources, review dates) | technical-writer+CSO | content/articles | — | todo | | | |
| S10-T95 | RAG pgvector, profile_id filter in code | ai-ml+backend | api knowledge/, migration | S10-T94 | todo | | | |
| S10-T96 | guardrails: dosing/prognosis/diagnosis block, emergency → 115 | ai-ml+safety | ai-gateway guardrails | — | todo | | | |
| S10-T97 | semantic cache + per-user token quota (SEC-AI-07) | mlops | ai-gateway | S10-T96 | todo | | | |
| S10-T98 | red-team set (100 Q + 50 injection images, synthetic) + pytest gate | qa+security | tests/redteam | S10-T96 | todo | | | |
| S11-T101 | timeline compare two visits | frontend | web features/timeline | S8-CLIN | todo | | | |
| S11-T102 | patient_reported text + NER → region (BR-040) | backend+ai-ml | api clinical/patient | S8-CLIN | todo | | | |
| S11-T103 | time-limited sharing, Cedar policies + tests (SEC-AR-07) | backend+security | api sharing/, policies | S8-CLIN | todo | | | |
| S11-T104 | share screen + clinician view watermark | frontend | web features/sharing | S11-T103 | todo | | | |
| S11-T105 | admin without PHI + break-glass (SEC-AZ-05) | backend+security | api admin/ | — | todo | | | |
| S11-T106 | DSR: export, consent withdrawal, deletion across stores | data-engineer+backend | api identity/patient dsr | S8-CLIN | todo | | | |
| S11-T107 | full regression + authorisation matrix | qa | docs/qa, api tests | S11-T106 | todo | | | |
| S11-T108 | eval report F1/Unit, ECE, region accuracy (synthetic 600) | ai-ml | ml/eval, docs/ai | S10-T92 | todo | | | |
| S11-T109 | user guide draft + internal release notes | technical-writer | docs/user-guide | late | todo | | | |
| S11-T110 | G2 evidence pack (sign-off human) | qc-release | docs/gates/G2.md | all | todo | | | |
| PM-RPT | sprint reports 06–11 (no fabricated demos/usability results) | product-manager | docs/project/reports | per sprint | todo | | | |
Human-only in scope: D79 CSO tooth/palette review, D87 usability test, D99 CSO article approval, G2/G2-CS sign-off, LIC-002.

### Run 5 progress (2026-10-24 ~02:35)
Extra rows: S10-T96 guardrails **merged** #101 (Opus: narrowed diagnosis regex false-blocks); S8-T74b odontogram viewer **merged** #105; S9-T82 GLB **merged** #104 (stylised procedural placeholder, real anatomy pending licence review; no Draco needed at ~120–150 KB); S10-T91 oncology BRs BR-046..051 READY #107 (draft, pending CSO D99).
In progress (batch 3): S8-CLIN (feat/S8-CLIN-clinical-projection), S9-T81/T83 3D viewer (feat/S9-T81-viewer-3d), S7-T61 prompt v2, S9-T89 headers/CORS, S10-T94 20 KnowledgeArticles (draft-pending-CSO), S10-T97 semantic cache + quota + HTTP traffic/locale.
Follow-ups noted: wire UploadScreen → /documents/[id]/progress and drop old STAGE map; web SSE needs fetch-streaming (EventSource can't send Authorization); per-user SSE stream cap with F7; pre-commit ruff older than CI ruff (formatting disagreement on multi-line asserts) → CHORE; deployment: RESULTS_BUCKET + consumer s3:GetObject extractions/*.

### Run 5 progress (2026-10-24 ~05:30)
Merged since last note (all reviewed with B4 + verdict, re-tested on head merged with main): #107 S10-T91 oncology BRs (draft pending CSO), #108 S10-T97 semantic cache + qa-only quota (round 2: cache hit needs equal numbers/negation), #109 S9-T81/T83 3D viewer, #110 S7-T61 prompt v2 (Opus: model bbox dropped), #111 S10-T94 20 KnowledgeArticles (draft-pending-CSO, sources unverified), #112 S8-CLIN clinical projection + findings API (migration 0006), #113 S9-T89 CSP/headers/CORS, #114 S9-T84 2D fallback, #115 S7-T62 normaliser (top-1 0.908 synthetic, OOV 3/16), #116 S11-T105 admin + break-glass (0006_admin), #117 S11-T101 timeline compare, #118 S8-T76/S9-T86/S10-T92 golden-v2 600 synthetic docs (no F1: no model predictions), #119 S10-T98 red-team gate, #120 S10-T95 RAG pgvector (0007), #121 BUG-10 red-team misses (100/100), #122 S7-T64b page image + bbox, #123 BUG-11, #124 S11-T103 sharing + Cedar (0008).
Ready: #125 S11-T102 patient-reported (Opus: migration → 0009, pyyaml declared).
Incident: #120 was merged with a red `python` check (gh merge does not require it) → main red ~20 min; fixed by BUG-11 #123. Merges are now gated on green python+web explicitly.
In progress: S11-T106 DSR, S11-T104 share UI, S7-T67/S9-T88 E2E + compat, S6-F7 rate limit.
Ops follow-ups for owner: pgvector extension on RDS (rds_superuser); API needs s3:GetObject+kms on pre/* and MEDILENS_S3_PAGES_BUCKET; NEXT_PUBLIC_STORAGE_ORIGIN must include the pages bucket origin; API and worker images must ship data/terminology; RESULTS_BUCKET + consumer s3:GetObject extractions/*; CI ruff (0.17.2) newer than pre-commit ruff → pin both (workflow/pre-commit change).

### Run 5 progress (2026-10-24 ~12:45, after 2nd and 3rd rate-limit resets)
Merged: #125 S11-T102 patient-reported (0009), #126 S7-T69 metrics mart (deployment needs an ADR-0006 definer for the cross-profile aggregate read → S7-T69b), #127 S8-T71 viewer state spec + D79 CSO kit (14 spec-vs-code gaps listed), #128 S11-T104 share UI (expiry shown from URL param → S11-T104b).
Resumed in existing worktrees after the limit: S11-T106 DSR (agent-a9ef02722f985e9db), S10-T93 onco summary + viewer gaps 1/2/13 (agent-af25171343116019a), S6-F7 (agent-a54427ede95cb61da), S7-T67/S9-T88 E2E (agent-a5ad2abc8652d590e). New: S11-T109 user guide + release notes, S11-T104b share expiry API.
Remaining after these: S11-T107 regression + authz matrix, S11-T108 eval report, S11-T110 G2 evidence pack, sprint reports 06–11, S6-T55b VietOCR (likely blocked: model download), S8-T78 visual regression, viewer gaps 4–12.

### Run 5 progress (2026-10-24 afternoon)
Merged: #129 S10-T93 oncology summary mode + patient_reported/unmapped labels, #130 S11-T109 user guide + internal release notes, #131 S6-F7 rate limit/quota/SSE cap, #132 S8-T78 viewer snapshots (Opus updated one snapshot after #129), #133 S11-T104b server-side share expiry, #134 S11-T108 eval report v1 (ECE + region accuracy; field F1 needs model predictions), #135 S7-T67/S9-T88 E2E + compat matrix (chromium/firefox/pixel7 4/4; webkit/iPhone not run: host libs), #136 BUG-12 oncology synonyms (region accuracy 1.000 on synthetic = upper bound), #137 S11-T106 DSR (export, consent withdrawal, erasure + verify; Opus resolved conflict with #131), #138 S8-GAPS viewer UX (Opus safety fix: no default caries).
In progress: S11-T107 regression + authz matrix, PM-RPT sprint reports 06–11, S6-T55b VietOCR (or blocker). Then S11-T110 G2 evidence pack and final verification.
