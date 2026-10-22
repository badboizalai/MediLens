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
| S2-T12 | D17 | OCR bake-off harness (CER, latency, USD/doc) + report on golden v0 | ai-ml-engineer | `ml/eval/ocr_bakeoff/` | S2-T11 | in-progress | feat/S2-T12-ocr-bakeoff |  |
| S2-T13 | D19 | DPIA v0 + data inventory + OTIA decision | regulatory-privacy-officer | `regulatory/privacy/` | S1-T02 | in-review: READY (stacked on #4) | docs/S2-T13-dpia-v0 | #12 |
| S1-T14 | D10 | Sprint-01 report, risk register (L×I), retro template | product-manager | `docs/project/reports/`, `docs/project/risk-register.md` | S1-T01 | in-review: READY (stacked on #5) | docs/S1-T14-risk-register | #9 |
| S2-F01 | — | Extend claims_lint for BR-042 phrases (+tests) | regulatory-privacy-officer | `.claude/skills/medilens-regulatory-privacy-officer/scripts/` | — | in-review: READY (round 2) | feat/S2-F01-claims-lint-rules | #19 |
| S2-F02 | — | Hazard check accepts project hazard-log columns | clinical-safety-officer | `.claude/skills/medilens-clinical-safety-officer/`, `safety/README.md` | — | in-review: READY (re-verified) | fix/S2-F02-hazard-check-columns | #17 |
| S2-F03 | — | Clinician interview guide + persona validation threshold | business-analyst | `docs/research/` | S1-T03 | in-review: READY (stacked on #6) | docs/S2-F03-clinician-guide | #16 |
| S2-F04 | — | BR traceability matrix | qa-engineer | `docs/requirements/` | S2-T08 | in-review: READY (stacked on #13) | docs/S2-F04-traceability | #18 |
| S2-F05 | — | Governance CI workflow + hazard-log notes column | cloud-devops-engineer | `.github/workflows/governance.yml`, `safety/hazard-log.csv`, `Makefile` | — | in-review: READY (**human merge**: workflow) | ci/S2-F05-governance-checks | #20 |
| S2-F06 | — | Handwriting + perspective variants for golden v0 | ai-ml-engineer | `ml/datasets/synth/`, `ml/eval/golden-v0/` | S2-T11 | in-review: READY (re-verified, stacked on #15) | feat/S2-F06-handwriting-variants | #21 |
| S2-F07 | D14 | Clickable low-fi HTML prototype of 8 screens | ux-ui-designer | `docs/ux/prototype/` | S2-T10 | in-progress | feat/S2-F07-clickable-prototype | |
| S2-T15 | D20 | Gate evidence packs G0 + G0-R (checklists, links, open items) for human sign-off | qc-release-gatekeeper | `docs/gates/` | all above | in-review: READY (G0/G0-R NOT YET READY — human items) | docs/S2-T15-gate-packs | #22 |

## Batches
- **Batch 1** (00:30): S1-T01, S1-T02, S1-T03, S1-T04, S2-T05, S2-T11 — 6 workers; 10 GB free RAM.
- **Batch 2** (~00:45): S2-T06, S2-T07, S2-T08, S2-T09, S2-T10, S2-T13, S1-T14 — 7 workers (docs-only, light); owner said "don't care about dates, fill tasks fast" → BRD/wireframes started from plan §2.4 without waiting for T07.
- **Batch 3** (~01:00): follow-ups from reviews S2-F01…F04.
- **Batch 4** (~01:10): S2-T12, S2-T15, S2-F05, S2-F06; then S2-F07 (prototype gap found by the G0 pack).

## PRs waiting for merge
Merge order matters (stacked): **#5 → #8, #9** · **#4 → #12, #19** · **#6 → #11, #16** · **#13 → #18** · **#15 → #21** · **#14 → (F07)** · #10, #17, #22 independent. **Human-only merges**: #7 (RULES), #20 (workflow).
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

## Handover
_written at stop_
