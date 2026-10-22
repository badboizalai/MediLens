# Quality Metrics

| Metric | Formula | Target |
| --- | --- | --- |
| Defect leakage | defects found in prod ÷ (found before release + in prod) | ≤ 10% |
| Escaped defects by severity | count per release | S1 = 0, S2 = 0 |
| Defect density | defects ÷ story points delivered | trending down |
| Change failure rate | releases causing incident/rollback ÷ releases | ≤ 15% |
| MTTR | mean time incident start → resolved | ≤ 4 h |
| Test pass rate (MUST suites) | passed ÷ total | 100% |
| Flake rate | flaky failures ÷ runs | ≤ 2% |
| AI correction rate drift | week-over-week change | within ±20% |
| User-reported issues | per 100 MAU per month | trending down |
