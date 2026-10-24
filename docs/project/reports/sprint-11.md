# Sprint 11 Report

Sprint dates: 2027-03-17 to 2027-03-30 (plan D101-D110; PRs merged 2026-10-23 to 2026-10-24) | Owner: PO/PM | Status: Draft (G2 review D110 not held)

## Goal
Feature complete for G2: timeline, patient-reported text, sharing, admin without PHI, data subject rights, evaluation report, user guide draft. Met: partly. Feature PRs are merged; the full regression and authorisation matrix is missing, model-dependent metrics cannot be measured yet, and the G2 sign-off is human-only.

## Delivered items
| Task | Item | PR | Status |
| --- | --- | --- | --- |
| D101 S11-T101 | Timeline comparing two visits | #117 | merged |
| D102 S11-T102 | Patient-reported findings with location NER | #125 | merged |
| D103 S11-T103 | Time-limited sharing with Cedar policies | #124 | merged |
| D104 S11-T104/104b | Share screen and watermarked clinician view; grantee sees server-side expiry | #128, #133 | merged |
| D105 S11-T105 | Admin without PHI and audited break-glass | #116 | merged |
| D106 S11-T106 | Data subject rights: export, consent withdrawal, deletion | #137 | merged |
| D108 S11-T108 | Evaluation report v1 with ECE and region accuracy on golden-v2 | #134 | merged (most metrics not measurable) |
| D109 S11-T109 | Draft user guide VI/EN and internal release notes | #130 | merged (draft) |

## Not delivered / carried over
- D107 full regression and authorisation matrix: no merged PR (only the S7-T67 E2E and the compat matrix).
- D108: field F1 overall, per Unit and per stratum, ECE value, end-to-end region accuracy, citation validity, FDI accuracy are n/m: no model was run, no predictions exist. Measured: mapper-only region accuracy 0.910 (oncology 0.769, FAIL vs 0.85), rules classifier macro-F1 1.000 (clean synthetic), LOINC top-1 0.908, red team 100/100.
- D110 `gates/G2.md`: not written; the gate cannot be claimed.
- Compat gaps: WebKit and iPhone 14 not run; OCR VietOCR not wired; ICD-10 not loaded (LIC-002).

## Human-only open items
- D110 G2 sign-off, and G2-CS (CSO review of the hazard log, dental and oncology wording, 20 articles).
- D99 CSO article approval; D79 CSO tooth/palette review; D87 usability test.
- LIC-002 (MoH ICD-10) and LIC-003 (LOINC) decisions; G0/G0-R and G1-D sign-offs as listed in `docs/gates/`.
- Terraform apply for staging; deployment grants.

## Top risks
| ID | Risk | Score | Change | Action |
| --- | --- | --- | --- | --- |
| R03 | Solo overload | 16 | none | Cut or defer rows listed above |
| R04 | LLM hallucination | 16 | none | Run a real model on golden-v2 to measure F1, ECE |
| R11 | Wrong region or side | 12 | trigger hit for oncology (0.769 < 0.85); synonyms added (#136) | Re-measure end to end |
| R07 | Law 91/2025 breach | 15 | DSR flows added (#137) | DPIA and overseas-transfer assessment stay human |

## Metrics
| Metric | This sprint | Previous | Target |
| --- | --- | --- | --- |
| Committed vs done (say/do) | 8 of 9 build rows (D101-D109) have a merged PR; D107 not delivered; D108 and D109 partial or draft | 7 of 9 (S10) | n/a |
| Velocity (rolling 3) | n/a | n/a | n/a |
| Open S1/S2 bugs | n/a (not measured) | n/a | 0 |
| Cloud + LLM cost (USD) | n/a (no LLM called) | n/a | n/a |
| Region accuracy, mapper only | 0.910 (n=1705, synthetic) | n/a | >= 0.85 |

## Retro
Based on `docs/operations/autopilot-state.md` and the run 5 notes relayed in the brief (state PR #97 is still a draft); human to confirm.
- Keep: reporting "n/m" instead of estimating when no model ran.
- Drop: unpinned tool versions (ruff version drift between local and CI broke checks).
- Try: pin ruff in the lockfile; keep one owner for migration order, because several PRs added migrations in parallel and had to be re-chained.

| Action | Owner | Due |
| --- | --- | --- |
| Pin ruff version; agree a migration numbering rule | PM | human to set |

## Learned
- A feature-complete count is not a gate pass; G2 needs measured model metrics and human sign-offs that do not exist yet.
