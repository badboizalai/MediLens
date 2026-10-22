# Test Strategy

## Pyramid (target share of automated tests)
Unit ~65% · Integration/contract ~25% · E2E/visual ~10%. Plus non-functional suites: performance, security (DAST/authz), accessibility, AI evaluation.

## Risk-based focus
| Risk area | Depth | Key suites |
| --- | --- | --- |
| PHI access control | Very high | Authz matrix, RLS tests, IDOR abuse cases, audit assertions |
| AI extraction correctness | Very high | Golden set eval, mapping/FDI unit tests, review-screen E2E |
| Medical safety (explanations) | Very high | Red-team set, guardrail tests |
| Sharing & expiry | High | Decision table tests with time travel |
| Viewer correctness | High | Visual baselines per Unit/severity, mapping consistency checks |
| Upload robustness | High | Boundary/negative file tests, malware sample (EICAR) |
| Performance | Medium | k6 scenarios |
| i18n | Medium | Snapshot of both locales, `i18n_check.py` (technical-writer skill) |
| Clinical safety requirements (CS-xxx) | Very high | One test per CS requirement, traced in the matrix (hazard log from the CSO skill) |
| New inputs (PDF/DOCX/FHIR/text/CT) | High | Malicious file sets, BR-040…045 tests, FHIR samples, emergency-text recall set |
| Special anatomy | High | 30 special-anatomy records, visual baselines per organ_status/device/precision |
| PHI boundary (SEC-AR) | Very high | Schema has no identity columns, API role cannot read clinical tables, worker has no internet, DEK deletion |
| AI cost/routing | Medium | Escalation and cost per document in eval runs (MLOps cost model) |

## Environments
local (Docker Compose + LocalStack) · CI ephemeral containers · staging (prod-like, synthetic data) · prod (smoke + synthetic monitoring only).

## Entry criteria (testing a story)
AC available, build deployed to test env, test data ready.

## Exit criteria (release)
All MUST tests pass; no open S1/S2; coverage thresholds met; AI gates pass; performance within NFR; a11y 0 serious; security suite pass; test summary report written.

## Defect severity
S1 data exposure, data loss, main flow blocked for all · S2 main flow broken for some/workaround hard, wrong medical display · S3 partial issue with workaround · S4 cosmetic.
