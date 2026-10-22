# Risk Register (seed)

Score = Likelihood (1–5) × Impact (1–5). ≥ 15 red.

| ID | Area | Risk | L | I | Score | Owner role | Mitigation | Trigger to act |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Safety | Users treat illustrations as diagnosis | 3 | 5 | 15 | ux-ui / qc | Disclaimers, wording, no prognosis, guardrails | Any user feedback implying self-treatment |
| R02 | Security | Health-data leak | 3 | 5 | 15 | security | Threat model, authz tests, RLS, encryption, synthetic data until audit | Any High finding open > SLA |
| R03 | Delivery | Solo overload, abandonment | 4 | 4 | 16 | pm | 3-Unit MVP, timebox, buffer 20% | Velocity drops 2 sprints in a row |
| R04 | AI | Hallucination | 4 | 4 | 16 | ai-ml | Schema, citations, human review, RAG on approved sources | Hallucination rate > 5% |
| R05 | AI | Poor OCR on handwriting/photos | 5 | 3 | 15 | ai-ml | Quality gate, capture tips, LLM vision fallback | CER > 20% |
| R06 | Data | No real data | 5 | 3 | 15 | ai-ml / data | Synthetic generator, public sets | Golden set < 200 docs at G2 |
| R07 | Legal | PDPL 91/2025 / Decree 356/2025 breach, cross-border transfer | 3 | 5 | 15 | security | Consent, DPIA, redaction, vendor choice | New provider or data purpose |
| R08 | Content | Wrong/outdated explanations | 3 | 4 | 12 | qc / ba | Sources, review dates, cron | Article overdue |
| R09 | Licensing | Asset/dataset licence violation | 3 | 3 | 9 | frontend / ai-ml | ATTRIBUTION.md, open licences | New asset without licence |
| R10 | FE | 3D lag on weak devices | 4 | 3 | 12 | frontend | Budgets, LOD, 2D fallback | FPS < 30 on test device |
| R11 | Mapping | Wrong region/side | 3 | 4 | 12 | ai-ml / frontend | Laterality rules, mapping tests | Region accuracy < 0.85 |
| R12 | Cost | LLM/cloud overspend | 3 | 3 | 9 | devops | Budgets, caching, quotas | 80% budget alert |
| R13 | Vendor | Model deprecated/changed | 3 | 3 | 9 | ai-ml | Adapter, nightly eval, pinned versions | Deprecation notice |
| R14 | Ops | Data loss | 2 | 5 | 10 | sre | Backups + verify, DR drill | Backup verify fails |
| R15 | Architecture | Over-engineering | 3 | 3 | 9 | architect | Modular monolith, K8s post-MVP | Infra work > 25% of sprint |
| R16 | Ethics/UX | Fear from cancer visuals | 3 | 4 | 12 | ux-ui | Summary mode, reassuring copy, support links | Negative usability feedback |
| R17 | Regulatory | Feature drifts into medical-device scope (detection, risk score, CT measurement) | 3 | 5 | 15 | regulatory-privacy-officer | Intended use, RDR, G0-R re-run, claims lint, BR-042 | Backlog item touching diagnosis/detection |
| R18 | Clinical safety | No real clinician available to sign G2-CS | 3 | 4 | 12 | clinical-safety-officer | Recruit advisor in S01, fallback mentor network, plan slack before beta | Advisor not confirmed by S04 |
| R19 | Data licence | Dataset used outside its licence (NC/DUA/SA) | 3 | 4 | 12 | data-curator | License Register before download, G1-D, license_register_check.py | Any dataset without decision |
| R20 | Data quality | Annotation agreement too low (kappa < 0.8) | 3 | 3 | 9 | data-curator | Calibration, guideline iterations, adjudication | Pilot kappa < 0.7 |
| R21 | Cost | Escalation to Tier L > 15% inflates token cost | 3 | 3 | 9 | mlops-engineer | Threshold tuning, prompt/schema fixes, caching, batch | Escalation > 15% for a week |
| R22 | Imaging | CT pipeline (GPU, registration error) slips v2.0 | 4 | 3 | 12 | medical-imaging-engineer | Template fallback, scale-to-zero GPU, cut to slice viewer + report linking | Registration error ≥ 15 mm at S23 |
| R23 | Privacy | Overseas processing without OTIA or consent C2 | 2 | 5 | 10 | regulatory-privacy-officer | OTIA within 60 days, consent screens, vendor DPA | New provider or region |
| R24 | Support | Safety signals from users missed after launch | 2 | 5 | 10 | support-success | Safety flag in taxonomy, CSO triage ≤ 1 working day, hypercare | Safety ticket older than SLA |
| R25 | Localization | VI/EN meaning differs for medical strings | 3 | 3 | 9 | technical-writer | Glossary, CSO review, i18n_check in CI | i18n errors or CSO findings |
