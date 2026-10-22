# Clinical Validation Protocol (synthetic records)

## Objective
Show that confirmed findings are placed on the correct region/side and that explanations are clinically acceptable, as judged by independent clinicians, before beta (G2-CS).

## Design
- Reviewers: ≥ 2 clinicians (or senior medical students supervised by a clinician), blinded to each other.
- Sample: ≥ 100 synthetic records, stratified: each MVP Unit (Dental, Cardiology, Oncology) ≥ 30, each main document type ≥ 10, include ≥ 10 special-anatomy cases and ≥ 10 handwritten/poor-photo cases.
- Materials: original record image/text, MediLens viewer screenshot, explanation text.
- Questions per item: (a) region correct? (b) side correct? (c) severity label consistent with the record? (d) explanation accurate and safe? (e) anything potentially harmful? (free text)

## Metrics
- Proportion correct per question with 95% confidence interval.
- Inter-rater agreement: Cohen's kappa (target ≥ 0.8; 0.6–0.8 acceptable with adjudication).
- Count of potentially harmful items (target 0 unresolved).

## Procedure
1. Freeze build and dataset version; record IDs.
2. Brief reviewers with the intended use and scoring guide.
3. Independent review (spreadsheet with one row per item).
4. Compute agreement; adjudicate disagreements with a third reviewer or the CSO.
5. Root-cause every error; link to hazards; create fixes or CS requirements.
6. Report `safety/validation/VAL-001.md`: sample, metrics, errors, actions, conclusion.

## Ethics and data
Synthetic or properly licensed de-identified data only. Reviewers sign an NDA and a short agreement on how their feedback is used. No real patient data before G3-P.
