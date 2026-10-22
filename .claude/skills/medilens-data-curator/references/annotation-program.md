# Annotation programme

## Roles
Annotation lead (you) · annotators (2–3 medical students) · adjudicator (clinician/CSO) · tool admin.

## Guideline content (template in assets)
Task definition · label schema (same JSON Schema as extraction) · decision rules · 10+ worked examples and counter-examples · edge cases (abbreviations, handwriting, unclear side, multiple findings) · when to mark "unsure" · escalation path · version history.

## Process
1. Calibration: all annotators label the same 20 items; discuss differences; update the guideline (v1.1).
2. Production: batches of 50; 15% overlap for agreement; spot checks by the lead.
3. Adjudication weekly; disagreements become guideline examples.
4. Metrics per batch: kappa (overlap items), lead-audit error rate, throughput, time per item.
5. Feedback to annotators within one week.

## Tooling
Label Studio (self-hosted in the dev account, synthetic/de-identified data only), SSO or individual accounts, no export rights for annotators, audit of access.

## People
NDA, assignment of rights, transparent pay per hour or item, no personal devices for real data, training on privacy. Never ask annotators to use their own credentialed access (e.g., PhysioNet) for project data.

## Cost estimate formula
items × minutes per item ÷ 60 × hourly rate × (1 + overlap share + adjudication share). Example inputs are project-specific; record them in the plan.
