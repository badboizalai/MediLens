# Clinical Risk Management (ISO 14971 style, adapted for a learning project)

MediLens is kept outside medical-device scope by its intended use, but it still shows health information to patients, so it applies the risk-management discipline used for medical software. Certification is not the goal; the habit and the evidence are.

## Contents
1. Process
2. Severity scale
3. Probability scale
4. Risk matrix and acceptability
5. Control hierarchy
6. Documentation and traceability
7. Review cadence

## 1. Process
Intended use (RDR) → hazard identification → risk estimation → risk evaluation → risk control (CS requirements) → verification of controls → residual risk evaluation → overall residual risk (safety case) → production and post-market information → back to hazard identification.

## 2. Severity (S)
| S | Name | MediLens example |
| --- | --- | --- |
| 1 | Negligible | Cosmetic error, no effect on understanding |
| 2 | Minor | Confusion resolved by reading the original record; mild anxiety |
| 3 | Moderate | User misunderstands a finding and delays a non-urgent check-up; significant distress |
| 4 | Major | User skips or changes prescribed care based on the app; missed urgent symptom routing |
| 5 | Critical | Plausible contribution to serious harm or death (e.g., emergency signs not routed to 115) |

## 3. Probability (P) of harm per use
| P | Name | Guide |
| --- | --- | --- |
| 1 | Improbable | Requires several independent failures |
| 2 | Remote | Single failure plus unusual user behaviour |
| 3 | Occasional | Single failure with common behaviour |
| 4 | Probable | Seen in testing more than rarely |
| 5 | Frequent | Expected in normal use |

## 4. Risk matrix (score = S × P)
| Score | Region | Rule |
| --- | --- | --- |
| 1–4 | Acceptable | Monitor |
| 5–9 | ALARP | Reduce as far as practicable; justify residual |
| 10–25 | Unacceptable | Must be reduced before release; G2-CS fails while any residual is here |
Additional rule: any residual with S = 5 needs explicit CSO sign-off even when P = 1.

## 5. Control hierarchy (prefer the top)
1. Inherent safety by design — do not show it (e.g., never render unconfirmed data; no prognosis feature at all).
2. Protective measures — confirmation steps, confidence highlighting, blocks, emergency routing, mismatch warnings.
3. Information for safety — labels, disclaimers, "you described" tags, help text.
Information alone is not adequate for S ≥ 4.

## 6. Documentation and traceability
- `safety/CRMP.md` plan; `safety/hazard-log.csv` (template in assets); `safety/CSC.md` safety case; `safety/validation/` study files.
- Each hazard `HZ-xxx` links to controls `CS-xxx`; each `CS-xxx` links to `TC-xxx` (verification) and, where validation applies, `VAL-xxx`.
- The BA traceability matrix gains columns UN, CS and VAL; `check_traceability.py` is reused.

## 7. Review cadence
Every sprint that changes clinical behaviour (W7) · every release (before QC gate) · quarterly hazard-log review · after every safety incident.
