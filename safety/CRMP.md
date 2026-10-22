# Clinical Risk Management Plan - MediLens v0.1 (DRAFT)

> **DRAFT - not approved.** Requires review and sign-off by a human clinician (clinical advisor). Until then no clinical-safety claim in this repository is valid, and gate G2-CS cannot pass.

| Field | Value |
| --- | --- |
| Intended use (from RDR) | Illustrate and explain a user's own medical records; never diagnose, dose or give prognosis (BR-042). Final wording pending the Regulatory Decision Record (G0-R). |
| Scope | MVP: upload (photo/PDF/digital/text), OCR + LLM extraction, user review, 2D/3D body viewer by `region_code`, 3 Units, explanations. v2 CT features are out of scope until this plan and G0-R are re-run. |
| Clinical Safety Officer | `<TBD clinical advisor>` (see Open items) |
| Reviewers | Regulatory & Privacy, QC |
| Standard basis | ISO 14971 style, adapted for a learning project (no certification claimed) |
| Evidence location | `safety/` (`hazard-log.csv`; later `CSC.md`, `validation/`) |

## 1. Roles
| Role | Holder | Duty |
| --- | --- | --- |
| Clinical Safety Officer (CSO) | `<TBD clinical advisor>` (1-2 h/month per project plan) | Owns this plan and the hazard log; reviews medical wording and severity display; signs the Clinical Safety Case at G2-CS; signs off any residual S = 5 |
| Skill owner (agent) | `medilens-clinical-safety-officer` | Drafts hazards, controls and records; cannot replace the human sign-off |
| Hazard owners | Role named per row in `hazard-log.csv` | Implement and verify controls |
| Regulatory & Privacy | `medilens-regulatory-privacy-officer` | Intended use, claims review |
| QC | `medilens-qc-release-gatekeeper` | Checks evidence before release gates |

### Fallback if no clinical advisor is recruited
- Real patient data, beta and public launch stay **blocked**; G2-CS cannot pass without a human clinician.
- Work continues on synthetic data only; every clinical statement is labelled "unreviewed draft".
- Interim reviewers (a medical friend, mentor or medical-student annotator) may give **advisory** comments recorded in review records, but do not sign the Safety Case.
- Reduce clinical surface: quote the record only, visualisation without explanations (the R01 contingency in the project plan), no oncology/metastasis Unit.
- Re-attempt recruitment each quarter; record the decision in the decision log.

## 2. Severity scale
| S | Name | Example |
| --- | --- | --- |
| 1 | Negligible | Cosmetic error, no effect on understanding |
| 2 | Minor | Confusion resolved by reading the original; mild anxiety |
| 3 | Moderate | Misunderstands a finding, delays a non-urgent check-up; significant distress |
| 4 | Major | Skips or changes prescribed care based on the app; missed urgent routing |
| 5 | Critical | Plausible contribution to serious harm or death |

## 3. Likelihood scale (per use)
| L | Name | Guide |
| --- | --- | --- |
| 1 | Improbable | Several independent failures needed |
| 2 | Remote | One failure plus unusual user behaviour |
| 3 | Occasional | One failure with common behaviour |
| 4 | Probable | Seen in testing more than rarely |
| 5 | Frequent | Expected in normal use |

## 4. Risk acceptability matrix (score = S x L)
| S \ L | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| 5 | 5 ALARP | 10 U | 15 U | 20 U | 25 U |
| 4 | 4 A | 8 ALARP | 12 U | 16 U | 20 U |
| 3 | 3 A | 6 ALARP | 9 ALARP | 12 U | 15 U |
| 2 | 2 A | 4 A | 6 ALARP | 8 ALARP | 10 U |
| 1 | 1 A | 2 A | 3 A | 4 A | 5 ALARP |

A = Acceptable (1-4, monitor) · ALARP (5-9, reduce as far as practicable and justify the residual) · U = Unacceptable (>= 10, must be reduced before release; G2-CS fails while any residual is here).
Extra rule: any residual with S = 5 needs explicit CSO sign-off even at L = 1. Information-only controls (labels, banners, disclaimers) are not adequate for S >= 4.

## 5. Control hierarchy
1. Inherent safety by design (do not show it; never render unconfirmed data; no prognosis feature).
2. Protective measures (confirmation, confidence highlighting, blocks, emergency routing, mismatch warnings).
3. Information for safety (labels, disclaimers, "you described" tags).

## 6. Activities per phase and gate
| Phase / gate | Activity | Output |
| --- | --- | --- |
| P0 Discovery (G0-R) | Intended-use input, this plan, seed hazard log | CRMP.md, hazard-log.csv |
| P1 Foundation | Hazard analysis per new input type; CS-xxx requirements into SRS; traceability columns UN/CS/VAL | updated log, CS list |
| P2 MVP sprints | Hazard analysis per feature/Unit; content and display review each sprint with clinical changes; verify controls (TC-xxx) | review records, test evidence |
| Before G2-CS | Clinical validation with clinicians; run `hazard_risk_check.py`; residual evaluation | VAL reports, check output |
| G2-CS (before beta) | No unacceptable residual risk; Clinical Safety Case signed by the human CSO | CSC.md |
| Each release | Re-assess changed areas before the QC gate | updated log |
| Post-market | Safety-report triage, monthly trend, hazard-log update | incident reports |
| Before v2 (CT) | Re-run this plan and G0-R; add CT hazards (catalog HZ-014/015) | updated plan |

## 7. Review cadence
Every sprint that changes clinical behaviour · every release (before QC gate) · quarterly full hazard-log review · after every safety incident · on any change to intended use.

## 8. Open items
- [ ] **Recruit the clinical advisor (human task).** Until done, the CSO field stays `<TBD clinical advisor>`.
- [ ] Clinician review of hazard scoring and this plan.
- [ ] Replace `TC-TBD` verification entries with real test ids.
- [ ] Add remaining catalog hazards (shared view, paediatric template, CT, conflicting sources, device glyphs) as those features are scoped; hazard ids in this log are local and may differ from the catalog numbering.

## Approval
| Name | Role | Date | Signature |
| --- | --- | --- | --- |
| `<TBD>` | Clinical Safety Officer | | |
