# Risk Register

Version 0.1 | 2026-10-23 | Owner: PO/PM (`medilens-product-manager`) | Task S1-T14

Score = Likelihood (1-5) x Impact (1-5). Score >= 15 is red. IDs match the [charter](../charter.md) top-5 (R01, R02, R03, R04, R07) and R18. Sources: `docs/plan/project-plan.en.md` section 11 (R01-R16) and the PM skill seed (R17-R25). Review at every sprint planning (D1).

The Response column holds the mitigation; plan contingencies are in plan section 11.

| ID | Area | Risk | Cause | L | I | Score | Owner role | Response | Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Safety | Users mistake illustrations for diagnosis and self-treat | Wording or UI implies a diagnosis or prognosis | 3 | 5 | 15 (red) | ux-ui / qc | Disclaimers on every screen, 'your record states...' wording, no prognosis, guardrails | Any user feedback implying self-treatment | Open |
| R02 | Security | Health-data leak (IDOR, misconfigured S3, leaked secrets) | Missing authz, weak config, secrets in repo | 3 | 5 | 15 (red) | security | Threat model, authz tests, RLS, encryption, secret scanning, synthetic data until audit | Any High finding open past SLA | Open |
| R03 | Project | Solo overload, burnout, abandonment | One person carries all roles | 4 | 4 | 16 (red) | pm | 3-Unit MVP, timeboxes, 20% buffer, retros, permission to cut scope | Velocity drops 2 sprints in a row | Open |
| R04 | AI | LLM hallucination | Model generates unsupported content | 4 | 4 | 16 (red) | ai-ml | Structured output + citations, human review, RAG on approved sources | Hallucination rate > 5% | Open |
| R05 | AI | Poor OCR on handwriting and bad phone photos | Low image quality, handwriting | 5 | 3 | 15 (red) | ai-ml | Image quality gate, capture tips, LLM vision / cloud OCR fallback | CER > 20% | Open |
| R06 | Data | No real data to train or evaluate | Real data barred before G3-P | 5 | 3 | 15 (red) | ai-ml / data-curator | Synthetic generator, public datasets, self-labelling | Golden set < 200 docs at G2 | Open |
| R07 | Legal | Breach of Law 91/2025 / Decree 356/2025 (sensitive data, cross-border via APIs) | Missing consent, DPIA or transfer assessment | 3 | 5 | 15 (red) | security / regulatory-privacy-officer | Consent, DPIA, PII redaction, vendor choice, OTIA within 60 days | New provider or data purpose | Open |
| R08 | Content | Wrong or outdated explanations | Stale or unreviewed articles | 3 | 4 | 12 | qc / ba | Authoritative sources, review dates, re-review cron | Article past review date | Open |
| R09 | Licensing | 3D/SVG assets or datasets violate licences | Asset used without recorded licence | 3 | 3 | 9 | frontend / ai-ml | ATTRIBUTION.md, open licences only | New asset without licence | Open |
| R10 | Frontend | Laggy 3D viewer on weak or mobile devices | Heavy meshes | 4 | 3 | 12 | frontend | Compression, LOD, size budget, 2D fallback | FPS < 30 on test device | Open |
| R11 | Mapping | Wrong region or side (left/right) | Ambiguous text, laterality errors | 3 | 4 | 12 | ai-ml / frontend | Laterality rules, mapping tests, show source text on click | Region accuracy < 0.85 | Open |
| R12 | Cost | LLM/cloud spend exceeds budget | Uncapped usage | 3 | 3 | 9 | cloud-devops | Caching, small models, budget alerts, daily upload caps | 80% budget alert | Open |
| R13 | Vendor | LLM provider changes pricing or retires a model | Provider dependency | 3 | 3 | 9 | ai-ml | Provider abstraction, nightly eval, pinned versions | Deprecation notice | Open |
| R14 | Operations | Data loss from failed migration or broken backup | Untested restore | 2 | 5 | 10 | sre | Expand/contract migrations, backup + verify, DR drills, PITR | Backup verify fails | Open |
| R15 | Engineering | Architecture too complex for one person | Early microservices or K8s | 3 | 3 | 9 | architect | Modular monolith, K8s post-MVP only | Infra work > 25% of sprint | Open |
| R16 | Ethics / UX | Cancer and metastasis visuals cause fear | Alarming colours or copy | 3 | 4 | 12 | ux-ui | Reassuring copy, summary-only mode, no prognosis figures, support links | Negative usability feedback | Open |
| R17 | Regulatory | Feature drifts into medical-device scope (detection, risk score, CT measurement) | Backlog creep | 3 | 5 | 15 (red) | regulatory-privacy-officer | Intended use, RDR, G0-R re-run, claims lint, BR-042 | Backlog item touching diagnosis or detection | Open |
| R18 | Clinical safety | No real clinician available to sign G2-CS | No advisor recruited | 3 | 4 | 12 | clinical-safety-officer | Recruit advisor in S01, fallback mentor network, slack before beta | Advisor not confirmed by S04 | Open (mitigating, close by S04) |
| R19 | Data licence | Dataset used outside its licence (NC/DUA/SA) | Download before licence decision | 3 | 4 | 12 | data-curator | License Register before download, G1-D, license_register_check.py | Any dataset without decision | Open |
| R20 | Data quality | Annotation agreement too low (kappa < 0.8) | Weak guidelines | 3 | 3 | 9 | data-curator | Calibration, guideline iterations, adjudication | Pilot kappa < 0.7 | Open |
| R21 | Cost | Escalation to Tier L > 15% inflates token cost | Thresholds too strict | 3 | 3 | 9 | mlops-engineer | Threshold tuning, prompt/schema fixes, caching, batch | Escalation > 15% for a week | Open |
| R22 | Imaging | CT pipeline (GPU, registration error) slips v2.0 | Registration accuracy, GPU cost | 4 | 3 | 12 | medical-imaging-engineer | Template fallback, scale-to-zero GPU, cut to slice viewer + report linking | Registration error >= 15 mm at S23 | Open |
| R23 | Privacy | Overseas processing without OTIA or consent | New vendor or region | 2 | 5 | 10 | regulatory-privacy-officer | OTIA within 60 days, consent screens, vendor DPA | New provider or region | Open |
| R24 | Support | Safety signals from users missed after launch | No triage path | 2 | 5 | 10 | support-success | Safety flag in taxonomy, CSO triage <= 1 working day, hypercare | Safety ticket older than SLA | Open |
| R25 | Localization | VI/EN meaning differs for medical strings | Literal translation | 3 | 3 | 9 | technical-writer | Glossary, CSO review, i18n_check in CI | i18n errors or CSO findings | Open |

## Red risks (score >= 15)

- R03 (16): Solo overload, burnout, abandonment
- R04 (16): LLM hallucination
- R01 (15): Users mistake illustrations for diagnosis and self-treat
- R02 (15): Health-data leak (IDOR, misconfigured S3, leaked secrets)
- R05 (15): Poor OCR on handwriting and bad phone photos
- R06 (15): No real data to train or evaluate
- R07 (15): Breach of Law 91/2025 / Decree 356/2025 (sensitive data, cross-border via APIs)
- R17 (15): Feature drifts into medical-device scope (detection, risk score, CT measurement)

## Change log

| Date | Change |
| --- | --- |
| 2026-10-23 | Initial register, 25 risks, all Open. |
