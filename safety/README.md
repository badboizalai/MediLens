# safety
Clinical risk management plan, hazard log, clinical safety case, validation (`medilens-clinical-safety-officer`).

| File | Purpose | Status |
| --- | --- | --- |
| `CRMP.md` | Clinical Risk Management Plan (ISO 14971 style) | DRAFT, awaiting clinician sign-off |
| `hazard-log.csv` | Hazard log seeded from the skill's hazard catalog | DRAFT, 16 hazards, all open |
| `CSC.md` | Clinical Safety Case (G2-CS) | not yet created |

`hazard-log.csv` uses the column names required by task S1-T04 (`id`, `hazard`, `likelihood`, ...). The skill's `scripts/hazard_risk_check.py` expects its own template names (`hazard_id`, `title`, `probability`, `cs_ids`, `notes`), so it must be run on a column-mapped copy until the script or template is aligned.
