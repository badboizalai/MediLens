# Sprint 10 Report

Sprint dates: 2027-03-03 to 2027-03-16 (plan D91-D100; PRs merged 2026-10-23 to 2026-10-24) | Owner: PO/PM | Status: Draft (review D100 not held)

## Goal
Oncology content rules and summary view, sourced KnowledgeArticles, RAG with profile-scoped retrieval, guardrails, semantic cache with quota, red-team gate. Met: partly. The engineering items are merged and the red-team gate passes on rules-level checks; articles are drafts and the CSO approval (D99) has not happened.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D91 S10-T91 | Oncology content rules and Gherkin | #107 | merged |
| D93 S10-T93 | Oncology summary mode and labelled findings | #129 | merged |
| D94 S10-T94 | 20 draft KnowledgeArticles VI/EN, pending CSO | #111 | merged (draft) |
| D95 S10-T95 | Knowledge RAG with pgvector and profile-scoped retrieval | #120 | merged |
| D96 S10-T96 | Safety guardrails: medicine amounts, outlook, condition naming, emergencies | #101 | merged |
| D97 S10-T97 | Semantic cache and per-user token quota | #108 | merged |
| D98 S10-T98 | Red-team gate: 100 unsafe + 30 benign questions, 50 injection PNG manifests | #119 | merged |
| BUG-10 | Red-team misses RT-001..005, RT-007 fixed (was 95/100) | #121 | merged |
| BUG-11 | pgvector image for migration-backed tests | #123 | merged |
| BUG-12 | Oncology and lymph-node location synonyms | #136 | merged |

## Not delivered / carried over
- D92 oncology extraction prompts (TNM, tumour site, nodes, metastases) and the 200-doc subset as a dedicated item: no merged PR; oncology golden docs came with #118 and location synonyms with #136.
- D99 CSO approval of the 20 articles, reassuring copy and disclaimers: not done (human).
- Red team limits (`tests/redteam/REPORT.md`): no real OCR or LLM ran (manifest text stands in for OCR); RT-006 (an obeying model that quotes the injected line) stays uncaught.
- D100 demo of cited Q&A: not run.

## Human-only open items
- D99 CSO approval of the 20 articles and copy; article review dates.
- D100 sprint review and retro.
- G2-CS (CSO review of `draft-pending-CSO` hazard rows).
- LIC-002 and LIC-003 licence decisions; Terraform apply for staging.

## Top risks
| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R01 | Illustration read as medical advice | 15 | mitigation added (#101, #119, #121) | Guardrails pass rules-level red team; real model not tested |
| R04 | LLM hallucination | 16 | none | Faithfulness not measured |
| R16 | Cancer visuals cause fear | 12 | mitigation added (#129 summary mode) | Needs usability feedback |
| R08 | Wrong or outdated explanations | 12 | none | Articles are drafts until D99 |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 7 of 9 build rows (D91-D99) have a merged PR; D94 is a draft; D92 not delivered, D99 human-only | 8 of 9 (S09) | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a | n/a | n/a |
| Red team: unsafe classified / benign blocked | 100/100 / 0 of 30 (rules level, `tests/redteam/REPORT.md`) | 95/100 before BUG-10 | >= 95 % / 0 |

## Retro
Based on `docs/operations/autopilot-state.md` and the run 5 notes relayed in the brief (state PR #97 is still a draft); human to confirm.
- Keep: a strict red-team gate that fails on new misses and on newly caught residuals.
- Drop: merging with red CI. #120 was merged with red CI because migration-backed tests needed a pgvector image; BUG-11 (#123) fixed it afterwards.
- Try: merge only on green CI, with no exceptions for follow-up fixes.

| Action | Owner | Due |
| --- | --- | --- |
| Enforce "no merge on red CI" in the merge step of `docs/operations/autopilot.md` | PM | human to set |

## Learned
- A red-team result at rules level says nothing about real model compliance; keep that caveat next to the number.
