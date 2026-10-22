# Release Gate Criteria

Release checks are numbered **RG-xx** to keep them distinct from the project's phase gates (G0–G6 plus G0-R, G1-D, G2-CS, G3-P, G5-H). `scripts/release_gate.py` evaluates them; the phase gates G3 (v1.0), G5 (v1.5) and G6 (v2.0) are decided by a GO from this checklist plus the phase-specific criteria in the sprint plan's Gates sheet.

| # | Criterion | Threshold | Overridable with risk acceptance? | Evidence owner |
| --- | --- | --- | --- | --- |
| RG-01 | Open S1 defects | 0 | No | QA |
| RG-02 | Open S2 defects | 0 | No | QA |
| RG-03 | Automated test pass rate (MUST suites) | 100% | No | QA |
| RG-04 | Backend coverage / frontend coverage | ≥ 80% / ≥ 70% | Yes (one release max) | BE / FE |
| RG-05 | Authorization matrix coverage | 100% | No | BE / Security |
| RG-06 | AI field F1 per Unit vs baseline | drop ≤ 1.0 point and ≥ 0.80 absolute | No | AI |
| RG-07 | Guardrail block rate / false block | ≥ 95% / ≤ 10% | No | AI |
| RG-08 | Hallucination rate | ≤ 5% | No | AI |
| RG-09 | API p95 on staging load test | ≤ 300 ms | Yes | QA / SRE |
| RG-10 | Accessibility serious/critical | 0 | Yes (with fix date ≤ 2 weeks) | FE |
| RG-11 | Security sign-off | GO | No | Security |
| RG-12 | Medical content reviewed for changed items | 100% | No | CSO / QC |
| RG-13 | DR drill within last 120 days | yes | Yes | SRE |
| RG-14 | Release notes + rollback plan ready | yes | No | PM / TW / DevOps |
| RG-15 | Clinical Safety Case signed; hazard log has 0 unacceptable residual risks (from G2-CS) | yes / 0 | No | CSO |
| RG-16 | Claims lint BLOCK findings on UI strings, landing, store text, prompts | 0 | No | Regulatory |
| RG-17 | Regulatory Decision Record current for the released scope (from G0-R) | yes | No | Regulatory |
| RG-18 | External pentest done with 0 open High/Critical when real data is in scope (from G3-P) | yes | No | Security |
| RG-19 | Data licence gate PASS for every dataset/model in the release (from G1-D) | PASS | No | Data Curator + Regulatory |
| RG-20 | AI cost per document ≤ budget and escalation to Tier L ≤ 15% | yes | Yes | MLOps |
| RG-21 | i18n check errors (VI/EN message files) | 0 | No | Technical Writer |

Metrics JSON fields are shown in `assets/release-metrics-example.json`; missing evidence counts as FAIL.
