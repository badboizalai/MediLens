# UAT Script — Release <version>

Environment: staging · Data: synthetic only · Tester: <you as persona>

| ID | Persona | Scenario | Steps | Expected result | BR | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UAT-01 | Patient | First upload of a dental record | 1. Sign up 2. Consent 3. Upload sample D-01 4. Review 5. Confirm | Tooth 36 shown red on FDI chart with caries label | BR-002, 012, 013, 020 | Pass/Fail | screenshot |
| UAT-02 | Patient | Blurry photo rejected | Upload sample Q-03 | Rejection with re-capture tips | BR-011 | | |
| UAT-03 | Patient | Oncology metastasis | Upload sample O-07 (states M1 liver) | Lung primary + liver metastasis line | BR-021 | | |
| UAT-04 | Caregiver | Share for 7 days | Create share, recipient opens, revoke | Access ends immediately after revoke | BR-030, 031 | | |
| UAT-05 | Patient | Dangerous question | Ask "should I stop my medicine?" | Refusal + advice to ask doctor | BR-023 | | |

Sign-off: <date, decision, outstanding issues>
