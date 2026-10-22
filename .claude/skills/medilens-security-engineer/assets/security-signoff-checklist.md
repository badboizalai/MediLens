# Security Sign-off — Release <version>

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | No Critical/High vulnerabilities open past SLA | | scanner report |
| 2 | gitleaks clean on release range | | CI run |
| 3 | SAST/SCA/IaC/container scans within thresholds | | CI run |
| 4 | SBOM generated for every image | | artefact |
| 5 | Threat model updated for new flows | | doc link |
| 6 | Authorization matrix covers 100% ID-based operations | | test report |
| 7 | Log scan finds no PHI/PII (`scan_log_for_pii.py` on staging logs) | | output |
| 8 | LLM security suite passed | | report |
| 9 | Security headers/CSP verified on staging | | scan |
| 10 | DAST (ZAP baseline) no High | | report |
| 11 | Security Hub score ≥ 90%, no Critical findings | | console export |
| 12 | Backups + restore tested this quarter | | DR record |

Decision: GO / NO-GO — <reason> — date
