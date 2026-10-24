# Sprint 07 Report

Sprint dates: 2027-01-13 to 2027-01-26 (plan D61-D70; PRs merged 2026-10-23 to 2026-10-24) | Owner: PO/PM | Status: Draft (review D70 not held)

## Goal
Review and confirm: extraction prompt v2 with citations, normalisation, findings API, review screen with the confirm gate, anatomy mapping, gateway cascade, first hazard log. Met: partly. Every build row has a merged PR, but ICD-10 mapping is gated, the hazard log is a draft, and no demo has been run.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D61 S7-T61 | Extraction prompt v2 with few-shots and line-anchored citations | #110 | merged |
| D62 S7-T62 | Terminology normaliser: abbreviations, LOINC subset (fuzzy match stands in for embeddings and rerank; ICD-10 interface only) | #115 | merged (partly) |
| D63 S7-T63 | Extraction review endpoints with ownership and audit | #72 | merged |
| D64 S7-T64/64b | Review screen with confirm gate (BR-012); source page image with bbox | #75, #122 | merged |
| D65 S7-T65 | Gateway cascade with confidence escalation and USD metering | #94 | merged (partly; prompt caching not evidenced) |
| D66 S7-T66/66b | Anatomy region mapping with FDI and laterality; map extracted findings | #83, #98 | merged |
| D67 S7-T67 | E2E upload-review-confirm flow and compat matrix | #135 | merged |
| D68 S7-T68 | Hazard log v1 draft (HZ-017..019 new, 6 updated, all `draft-pending-CSO`) | #80 | merged (draft, not a sign-off) |
| D69 S7-T69 | Pipeline metrics mart with daily data-quality checks | #126 | merged |

## Not delivered / carried over
- ICD-10 mapping: blocked by LIC-002; no code is loaded or emitted.
- D67: the authorisation matrix is one E2E case (another user's document returns 404); the full matrix is S11-T107, not delivered.
- D70 demo (edit and confirm): not run.

## Human-only open items
- D68: CSO review of hazard rows marked `draft-pending-CSO`; G2-CS stays human.
- D70 sprint review and retro.
- LIC-002 and LIC-003 licence decisions (ICD-10, LOINC).
- Terraform apply for staging.

## Top risks
| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R11 | Wrong region or side | 12 | mitigation added (#83, #98) | Mapper accuracy measured in S11: 0.910 overall, oncology 0.769 |
| R04 | LLM hallucination | 16 | none | Citations in #110; rate not measured, no model run |
| R03 | Solo overload | 16 | none | Say/do tracked below |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 9 of 9 build rows (D61-D69) have a merged PR; 6 complete, 3 partial (D62, D65, D68) | 9 of 9 (S06) | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a | n/a | n/a |

## Retro
Based on `docs/operations/autopilot-state.md` run 3 and run 4; human to confirm.
- Keep: safety fixes found in review before merge (#83 bilateral locations fall back to a group node).
- Drop: spec drift; BR-012 said 422 while the API returned 409 until BUG-06 (#88).
- Try: check spec and API status codes in the PR that introduces the endpoint. Run 4 hit a session limit about 20:50; five workers resumed after 21:30 and S7-T65 restarted.

| Action | Owner | Due |
| --- | --- | --- |
| Add a spec-vs-API status code check to the PR review checklist | PM | human to set |

## Learned
- Hazard rows recorded as drafts stay drafts until a clinician signs; do not count them as evidence.
