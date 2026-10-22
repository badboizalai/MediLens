# Vietnam Personal Data Protection — Compliance Map (learning summary)

Status as of 2026: the **Law on Personal Data Protection No. 91/2025/QH15 (PDPL)** was passed on 26 June 2025 and took effect on 1 January 2026; it unifies rules previously in **Decree 13/2023/ND-CP**. Consents, DPIAs and transfer assessments made under Decree 13 remain valid, but updates after 1 January 2026 must follow the PDPL. **Decree 356/2025/ND-CP** guides the PDPL, takes effect on the same date and replaces Decree 13/2023; it sets the forms (e.g., Form 08 breach notice, Form 09 transfer impact assessment, Form 10 processing impact assessment) and DPO qualifications. Always check the current official texts. This is not legal advice.

Health data is treated as sensitive personal data; for healthcare, consent is the required basis for processing health data, with narrow exceptions (e.g., protecting life/health in emergencies).

| Obligation | What it means for MediLens | Implementation | Evidence |
| --- | --- | --- | --- |
| Consent | Voluntary, informed, specific to each purpose; not bundled with unrelated services; withdrawable | Separate health-data consent (BR-002), per-purpose toggles (e.g., opt-in for evaluation BR-034), `consents` table with version | Consent records |
| Notice | Purpose, data types, processing methods, recipients, retention, rights, risks | Privacy policy + just-in-time notices | Policy versions |
| Minimisation & purpose limitation | Only what is needed to display/explain records | Optional profile fields; no training without opt-in | DPIA |
| Data subject rights | Access, correction, deletion, restriction, objection, withdrawal, portability | Settings flows; DSR SLA (BR-036) | DSR log |
| DPIA | Prepare and submit to the data protection authority within 60 days of starting processing | `assets/dpia-template.md` | Submission record |
| Overseas transfer (OTIA) | Transfers abroad (AWS Singapore, foreign AI APIs) need a separate overseas-transfer impact assessment submitted within 60 days of starting the transfer | Data-flow inventory, vendor assessments, PII redaction, region choice | OTIA dossier |
| Security measures | Technical + organisational measures for sensitive data | SEC catalog | Evidence pack |
| Breach notification | Notify the authority (A05, Ministry of Public Security) within 72 hours of detection using Form 08 (Decree 356/2025) and inform affected people where required | Incident Response Plan | Incident records |
| Children's data | Guardian consent; age checks | BR-001 | Consent records |
| Responsible person/department | Designate data protection responsibility | Documented role (you) | Org doc |
| Penalties awareness | Significant fines, including revenue-based fines for cross-border violations | Treat compliance items as MUST | — |

International good-practice references: HIPAA Security Rule safeguards; GDPR Art. 25 (privacy by design), Art. 30 (records), Art. 33 (breach notice), Art. 35 (DPIA).

Sources: Law No. 91/2025/QH15 (luatvietnam.vn English text); Allen & Gledhill, "Upcoming changes to Vietnam's personal data protection regime" (21 Aug 2025).
