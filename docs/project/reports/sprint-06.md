# Sprint 06 Report

Sprint dates: 2026-12-29 to 2027-01-12 (plan D51-D60; PRs merged 2026-10-22 to 2026-10-24, ahead of the plan calendar) | Owner: PO/PM | Status: Draft (facts from merged PRs; review D60 not held)

## Goal
Upload to processing: secure upload, status API with realtime events, page classification, OCR pre-processing, progress screen. Met: partly. The upload, pipeline hand-off and progress screen are merged; VietOCR for printed lines is not wired, the upload security review is PARTIAL, and no demo has been run.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D51 S6-T59 | Upload user stories (progress/retake stories not evidenced) | #40 | merged (partly) |
| D52 S6-T52 | Upload and progress screens | #58 | merged |
| D53 S6-T53 | ADR-0005 hand-off, accepted in #85 | #65, #85 | merged |
| D53 S6-T53a/f | api-events queue and IAM; job/event JSON Schemas | #68, #71 | merged |
| D53 S6-T53b/c | Chained steps with status events; result export and `extraction.completed` | #73, #82 | merged |
| D53 S6-T53d/d2 | API consumer applying status; ingest via definer function | #84, #106 | merged |
| D53 S6-T53e | Status SSE stream | #102 | merged |
| D54 S6-T54a/b/c | Rules page classifier; Unit picked in extract; 9-type synthetic set and eval | #76, #86, #90 | merged |
| D55 S6-T55 | Edge detection and perspective warp | #74 | merged (VietOCR part not delivered) |
| D56 S6-T56 | Processing progress screen with retake guidance | #99 | merged |
| D57 S6-T57/57b | Malicious upload file set; rejected status | #69, #78 | merged |
| D58 S6-T58 | Upload review vs SEC-AP-07 (PARTIAL); follow-ups F2, F3/F4, F9b, F4b | #77, #81, #79, #87, #89 | merged |
| D59 S6-T59 | Capture guide VI/EN | #40 | merged (glossary not evidenced) |
| S6-F7 | Upload rate limit, daily quota, SSE stream cap (review finding F7) | #131 | merged |
| BUG-01..06, 08, 09 | Auth problem types, status GET, worker wiring, stores, outbox relay, validate step, 422 with `field_ids`, terminal guard, SQL/npm advisories | #62, #61, #60, #63, #70, #67, #88, #92, #103 | merged |
| CHORE-01, CHORE-02 | Web env docs; ADR-0006 | #59, #85 | merged |

## Not delivered / carried over
- S6-T55b VietOCR for printed lines and CER re-run: no merged PR. The OCR bake-off measured vietocr CER 4.40 % and paddle 15.63 % on golden-v0 (`docs/ai/eval-report-v1.md`), but the worker does not use it yet.
- D58: `scan_log_for_pii.py` on staging logs not run (no staging deployed). The review verdict was NO-GO for real data until findings F1-F4 and F6 close; F10-F12 stay open.
- D54: an independent template set is needed before the classifier score (1.000, clean synthetic text) counts as G2 evidence.
- D51/D59: progress and retake stories, and the initial glossary, not evidenced in #40.
- D60 demo (upload to realtime OCR): not run.

## Human-only open items
- D60 sprint review demo and retro.
- Terraform apply for staging (AWS credentials, remote state, `kms_admin_role_arns`, environment reviewers); `GRANT api_events_consumer` at deployment.
- LIC-002 (MoH ICD-10) and LIC-003 (LOINC) licence decisions.
- `apps/web/.env.example` (blocked by deny rule); consent-form wording lines 6 and 27 (regulatory owner).

## Top risks
Take from [risk-register.md](../risk-register.md).

| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R02 | Health-data leak | 15 | none | Upload review is PARTIAL; close F1-F4, F6 before real data |
| R05 | Poor OCR | 15 | none | Wire VietOCR; measure on phone photos |
| R03 | Solo overload | 16 | none | Say/do tracked below |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 9 of 9 build rows (D51-D59) have a merged PR; 5 complete, 4 partial. D60 is this report | n/a | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a | n/a | n/a |

## Retro
Based on `docs/operations/autopilot-state.md` run 3 and run 4; human to confirm.
- Keep: real review comments on every PR; the orchestrator re-tests each head merged with main; an ADR before implementing the hand-off.
- Drop: starting dependent tasks before the blocking decision (the RLS access model stalled #84 for one run).
- Try: ask workers to leave a resumable note before a session limit (run 3 hit the limit about 12:45, reset 16:30; four workers were continued by fresh workers).

| Action | Owner | Due |
| --- | --- | --- |
| Write the resumable-note step into `docs/operations/autopilot.md` | PM | human to set |

## Learned
- A security review that ends PARTIAL produces a chain of follow-up PRs (#79, #81, #87, #89, #131); budget for them.
