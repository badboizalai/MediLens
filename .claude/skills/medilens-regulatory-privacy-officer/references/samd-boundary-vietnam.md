# Medical-device boundary (SaMD) — Vietnam

Status note: verify the current consolidated texts before relying on this summary; it reflects the plan's research as of 2026.

## Legal anchors
- Decree 98/2021/ND-CP on medical device management, amended by Decree 07/2023/ND-CP and Decree 04/2025/ND-CP. The definition of a medical device covers software used for medical purposes such as diagnosis, prevention, monitoring or treatment support.
- Circular 05/2022/TT-BYT (and later amendments): classification of medical devices into risk classes A–D by rules that depend on intended use.
- Circular 13/2025/TT-BYT: electronic medical records in health facilities (hospitals by 30/9/2025, other facilities by 31/12/2026). It does not create a patient-facing API right; third-party access depends on each facility.
- International references used for good practice: IMDRF SaMD framework, IEC 62304, ISO 14971, IEC 62366-1, ISO 13485.

## Decision questions (answer each with evidence)
1. Does any function produce a diagnosis, differential, triage level or risk score? 
2. Does any function analyse images or signals to detect, measure or characterise disease?
3. Does any function recommend, adjust or stop a treatment or medication?
4. Does any function monitor a physiological parameter to alert on deterioration?
5. Is the output intended to drive a clinical decision by a clinician?
6. Is marketing or UI wording claiming any of the above?
If all answers are "no" and the product only re-presents information already in the user's own records with sourced educational content, record the reasoning that MediLens is outside device scope for this version — and keep it that way through claims control.

## Features that move MediLens toward a device (need a new RDR and expert advice)
Automated lesion detection or measurement on CT/X-ray/skin photos · risk scores · symptom checkers that suggest conditions · treatment or dose suggestions · alerts on lab trends · clinician-facing decision support.

## How MediLens stays outside
BR-042 (CT for illustrative anatomy only), BR-022/023 (no dosing/prognosis), BR-040 (patient text not coded), claims lint in CI, CSO content review, intended use shown in the app's About page.

## When to get professional advice
Before commercial launch; before any feature in the list above; before working with a hospital; if a regulator, partner or user asks whether MediLens is a medical device.
