# Personal data protection duties — PDPL 91/2025/QH15 + Decree 356/2025/ND-CP

Both took effect on 1 January 2026; Decree 356/2025 guides the Law and replaced Decree 13/2023. Health data is sensitive personal data. Educational summary — check the official texts and get legal advice for real data.

| Obligation | MediLens implementation | Evidence |
| --- | --- | --- |
| Lawful basis; explicit, specific consent for sensitive data | Purpose-separated consent screens (BR-002); Consent entity with version + timestamp | Consent records, screenshots |
| Notice to data subjects | Privacy notice VI/EN: purposes, data types, recipients/processors, overseas processing, retention, rights, contact | Published notice + version history |
| Purpose limitation and minimisation | Only fields needed for the viewer; no ID numbers stored; analytics on pseudonymised gold tables | Data dictionary, catalog |
| Processing impact assessment (DPIA) | DPIA before processing real data; Form 10 dossier; filed within 60 days of starting processing | `privacy/DPIA-vN.md` + filing proof |
| Overseas transfer impact assessment (OTIA) | AWS ap-southeast-1 and LLM providers = processing abroad; Form 09 dossier; filed within 60 days of starting transfer | `privacy/OTIA.md` + filing proof |
| Data protection officer / department | Named DPO (the learner for practice; qualified person before real data) | Appointment record |
| Security measures | SEC catalog, PHI Service design (section 24), encryption, access control, audit | Security Evidence Pack |
| Breach notification | Notify the authority within 72 hours of detection (Form 08); inform affected people when required | Incident records |
| Data subject rights (access, correction, deletion, restriction, withdrawal of consent, objection, portability where applicable) | DSR flows (PB-06), identity verification, deadlines per the Decree | DSR log |
| Processor contracts | DPA with AWS/LLM/email providers: instructions, security, sub-processors, deletion, no training on our data | Signed terms, vendor assessments |
| Retention and deletion | Retention matrix; crypto-shredding; backups expiry | Retention matrix, deletion runs |
| Children's data | Profiles for minors created only by guardians (BR-001) with guardian consent | Consent records |
| Records and accountability | Records of processing, policies, training log | `privacy/` folder |

Penalties under the Law can be significant (including revenue-based fines for some violations); treat compliance gaps as release blockers, not paperwork.
