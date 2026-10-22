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
| S1-T01 | D01–D02 | Project charter + business case (incl. do-nothing) + stakeholder register + governance | product-manager | `docs/project/` | — | in-progress | | |
| S1-T02 | D03–D04 | Intended Use Statement + forbidden-claims list + Regulatory Decision Record RDR-001 | regulatory-privacy-officer | `regulatory/` | — | in-progress | | |
| S1-T03 | D05–D06 | User research kit: research plan, interview guide, consent form, anonymised note template, PII checklist | business-analyst | `docs/research/` | — | in-progress | | |
| S1-T04 | D09 | Clinical Risk Management Plan + hazard log (ISO 14971 style) seeded with known hazards | clinical-safety-officer | `safety/` | — | in-progress | | |
| S2-T05 | D16 | License Register for planned sources + validation with `license_register_check.py` | data-curator | `data/license-register.csv`, `data/catalog/` | — | in-progress | | |
| S2-T11 | D15 | Synthetic record generator + golden set v0 (50 docs, 3 Units, degradations) + Dataset Card + schema validation | ai-ml-engineer | `ml/datasets/`, `ml/eval/golden-v0/` | — | in-progress | | |
| S2-T06 | D18 | ADR-001 modular monolith, ADR-006 hybrid OCR, ADR-012 region + Bedrock availability | solution-architect | `docs/architecture/adr/` | — | todo | | |
| S2-T07 | D11 | Problem statement + MoSCoW, MVP locked to 3 Units | business-analyst | `docs/product/` | S1-T01 | todo | | |
| S2-T08 | D12 | BRD v1: To-Be BPMN, BR-001…BR-045, VI–EN glossary | business-analyst | `docs/brd/` | S2-T07 | todo | | |
| S2-T09 | D08 | Proto-personas + As-Is journey (hypotheses to validate) | ux-ui-designer | `docs/ux/personas/` | S1-T03 | todo | | |
| S2-T10 | D13–D14 | IA/sitemap + low-fi wireframes (8 screens) + prototype test script | ux-ui-designer | `docs/ux/wireframes/` | S2-T07 | todo | | |
| S2-T12 | D17 | OCR bake-off harness (CER, latency, USD/doc) + report on golden v0 | ai-ml-engineer | `ml/eval/ocr_bakeoff/` | S2-T11 | todo | | |
| S2-T13 | D19 | DPIA v0 + data inventory + OTIA decision | regulatory-privacy-officer | `regulatory/privacy/` | S1-T02 | todo | | |
| S1-T14 | D10 | Sprint-01 report, risk register (L×I), retro template | product-manager | `docs/project/reports/`, `docs/project/risk-register.md` | S1-T01 | todo | | |
| S2-T15 | D20 | Gate evidence packs G0 + G0-R (checklists, links, open items) for human sign-off | qc-release-gatekeeper | `docs/gates/` | all above | todo | | |

## Batches
- **Batch 1** (00:30): S1-T01, S1-T02, S1-T03, S1-T04, S2-T05, S2-T11 — 6 workers; 10 GB free RAM.

## PRs waiting for human merge
_none yet_

## Decisions
- 2026-10-23: Sprint 1–2 follow the 52-week sheet (P0 Discovery), not the older §5.1 build sprints.
- 2026-10-23: AI never approves or merges PRs; Opus reviews with `--comment` plus a verdict, and the human merges (RULES A3).

## Blockers
_none_

## Helper tools used
_empty_

## Handover
_written at stop_
