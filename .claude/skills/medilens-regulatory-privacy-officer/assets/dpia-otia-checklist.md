# DPIA / OTIA checklist (PDPL 91/2025 + Decree 356/2025)

## DPIA (processing impact assessment — Form 10)
- [ ] Controller/processor details, DPO contact
- [ ] Purposes and legal basis per purpose (explicit consent for health data)
- [ ] Data categories (C4 PHI, C3 PII), data subjects (adults, minors via guardians)
- [ ] Data flows incl. processors (AWS, LLM, email) and sub-processors
- [ ] Retention per category; deletion method (crypto-shredding)
- [ ] Risks to data subjects and mitigations (link SEC/PHI Service design)
- [ ] Rights handling (DSR process)
- [ ] Prepared before real processing; filed within 60 days of starting processing

## OTIA (overseas transfer impact assessment — Form 09)
- [ ] Recipient(s) abroad: AWS Singapore region, LLM provider region(s)
- [ ] Purpose of transfer, data categories, volume
- [ ] Safeguards: encryption, access control, contracts (DPA), no training clause
- [ ] Risk assessment and mitigations
- [ ] Data subject consent covers overseas processing
- [ ] Filed within 60 days of starting the transfer; update when recipients/purposes change
