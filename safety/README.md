# safety
Clinical risk management plan, hazard log, clinical safety case, validation (`medilens-clinical-safety-officer`).

| File | Purpose | Status |
| --- | --- | --- |
| `CRMP.md` | Clinical Risk Management Plan (ISO 14971 style) | DRAFT, awaiting clinician sign-off |
| `hazard-log.csv` | Hazard log seeded from the skill's hazard catalog | DRAFT, 19 hazards, pending CSO review (see `hazard-log-v1-notes.md`) |
| `CSC.md` | Clinical Safety Case (G2-CS) | not yet created |

`hazard-log.csv` uses the column names required by task S1-T04 (`id`, `hazard`, `likelihood`, ...). The skill's check script accepts them directly (and the older template names via an alias map). Run:

```
python3 .claude/skills/medilens-clinical-safety-officer/scripts/hazard_risk_check.py safety/hazard-log.csv
```
