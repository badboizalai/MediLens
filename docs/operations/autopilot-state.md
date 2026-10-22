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
