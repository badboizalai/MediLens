# Security Requirements Catalog v1 (2026-10-23)

Task S3-F16. Owner: security-engineer. Statements come from `docs/plan/project-plan.en.md` sections 13 and 24.6; risks from `docs/security/threat-model.md`.
Every `SEC-xx` code found in `docs/` and code comments is listed once. Frontend codes FE-SEC-01..06 (plan 18.6) belong to frontend-engineer and are not repeated.

## Status definitions
- planned: no code or config on `main` enforces it.
- implemented: code or IaC exists on `main`, but the check does not fully cover the statement, or the IaC is not yet applied to an account.
- verified: an automated test or CI scan on `main` exercises the statement. It does not mean residual risk is accepted.

Evidence paths are relative to the repo root and exist on `origin/main`. Verification prefix: test, scan or review.
CI controls backing several codes: Semgrep, pip-audit and Trivy in `.github/workflows/security.yml`; gitleaks in `.github/workflows/ci.yml`.
New requirements from threat-model open items: SEC-AP-07a (O-01), SEC-AI-10 (O-02), SEC-AI-02a (O-03).


## Identity and session (SEC-ID)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-ID-01 | OIDC Authorization Code + PKCE only; no Implicit flow | Prevents token leakage via redirects | review: IdP config; E2E | security-engineer | planned | - |
| SEC-ID-02 | Passwords >= 12 chars, breached-password check, no forced rotation | NIST 800-63B credential hygiene | test: unit | security-engineer | planned | - |
| SEC-ID-03 | MFA mandatory for Clinician and Admin; mandatory for Patient when sharing is on | Limits account takeover of accounts reaching shared PHI | test: E2E per role | security-engineer | planned | - |
| SEC-ID-04 | JWT access tokens <= 15 min, RS256/ES256; rotating refresh tokens with reuse detection | Shrinks stolen-token window | test: integration | backend-engineer | implemented | `apps/api/tests/identity/test_auth.py`; `apps/api/src/medilens/modules/identity/application/token_validator.py` (access-token validation only; refresh rotation not built) |
| SEC-ID-05 | Session cookies HttpOnly, Secure, SameSite; no tokens in localStorage | Blocks XSS token theft | scan: header scan; FE test | frontend-engineer | planned | - |
| SEC-ID-06 | Lockout after 5 failures, per IP+account rate limits, CAPTCHA after 3 | Brute force and credential stuffing | test: k6 | security-engineer | planned | - |
| SEC-ID-07 | Sign out all devices; active sessions list | User can recover from compromise | test: E2E | backend-engineer | planned | - |
| SEC-ID-08 | Email alert on new device/country, password or MFA change | Lets the user notice a takeover sooner | test: E2E | backend-engineer | planned | - |
| SEC-ID-09 | Clinician registration verified (licence upload, Admin approval); to be MUST before clinician shares (threat model O-04) | Fake clinician could receive shares (S-06) | review: process + audit | product-manager | planned | - |

## Authorization (SEC-AZ)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-AZ-01 | Deny by default: every endpoint authenticated with explicit policy | Prevents forgotten unauthenticated routes | scan: route listing fails CI | backend-engineer | planned | - |
| SEC-AZ-02 | Ownership check in service layer for every ID-based query | Anti-IDOR/BOLA | test: user A requests user B -> 404 | backend-engineer | planned | template: `.claude/skills/medilens-backend-engineer/assets/test-authz-template.py` |
| SEC-AZ-03 | PostgreSQL RLS by profile_id as second layer | Defence in depth if app check is missed | test: SQL tests as app role | backend-engineer | verified | `apps/api/tests/db/test_rls_and_migration.py` (test_rls_isolates_profiles, test_app_ro_cannot_write) |
| SEC-AZ-04 | Share scope + expiry checked at access time, cache <= 60 s | Revocation must take effect quickly | test: integration | backend-engineer | planned | - |
| SEC-AZ-05 | Admins cannot read PHI; break-glass needs reason, 1 h, alert, audit | Limits insider access | test: E2E + alert check | security-engineer | planned | - |
| SEC-AZ-06 | Separation of duties for medical content approval | Prevents self-approved clinical content | test: workflow | product-manager | planned | - |
| SEC-AZ-07 | Mass assignment prevented: DTO allowlists only | Prevents privilege/field injection | test: contract | backend-engineer | planned | - |

## Data protection (SEC-DP)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-DP-01 | TLS 1.2+ everywhere incl. RDS; HSTS 1 year | Confidentiality in transit | scan: SSL Labs; rds.force_ssl | cloud-devops-engineer | planned | partial IaC: `infra/terraform/modules/rds-postgres/main.tf` |
| SEC-DP-02 | KMS customer-managed keys for RDS, S3, EBS, backups, SQS; yearly rotation | Key control and revocation | scan: AWS Config rule | cloud-devops-engineer | implemented | `infra/terraform/modules/storage/main.tf` (S3 CMKs; other stores not yet covered) |
| SEC-DP-03 | Application-level envelope encryption for identifiers | DB dump is unreadable | test: unit + unreadable dump | backend-engineer | verified | `apps/phi-service/tests/test_phi.py` (roundtrip, stored-encrypted, tamper tests); `apps/phi-service/src/medilens_phi/crypto.py` |
| SEC-DP-04 | S3 Block Public Access, TLS-only policy, BucketOwnerEnforced, versioning + Object Lock for audit | Prevents public exposure and tampering | scan: AWS Config, Access Analyzer | cloud-devops-engineer | implemented | `infra/terraform/modules/storage/main.tf` (not applied; Object Lock on audit bucket not yet) |
| SEC-DP-05 | Presigned URLs <= 5 min with content-type and size limits | Limits stolen-URL abuse | test: integration | backend-engineer | planned | - |
| SEC-DP-06 | No PHI/PII in logs, traces, error tracking; redaction middleware + log scan | Logs are widely readable | scan: automated log scan | backend-engineer | implemented | `apps/phi-service/tests/test_phi.py` (test_no_phi_in_logs); `apps/ai-gateway/tests/test_gateway.py` (test_logs_contain_no_raw_pii); repo-wide log scan not yet |
| SEC-DP-07 | Dev/staging synthetic data only; prod snapshot copy-down blocked | Real data must not leave prod | scan: SCP | cloud-devops-engineer | planned | related SCPs: `infra/terraform/org/scp/deny-disable-security-services.json`; snapshot-sharing SCP not yet |
| SEC-DP-08 | Deletion by crypto-shredding (delete user data key) | Backups covered | test: runbook + test | backend-engineer | verified | `apps/phi-service/tests/test_phi.py` (test_crypto_shred_makes_data_unreadable) |
| SEC-DP-09 | Dynamic watermark on shared images | Deters leaks by recipients | test: E2E | frontend-engineer | planned | - |

## Application (SEC-AP)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-AP-01 | Validate input with schemas; reject unknown fields | Injection and malformed input | test: contract + schemathesis | backend-engineer | planned | - |
| SEC-AP-02 | ORM/parameterised queries only | SQL injection | scan: Semgrep rule | backend-engineer | implemented | `.github/workflows/security.yml` (Semgrep ERROR blocks; no dedicated SQL-concat rule yet) |
| SEC-AP-03 | React escaping; dangerouslySetInnerHTML only via DOMPurify | XSS | scan: ESLint rule | frontend-engineer | planned | - |
| SEC-AP-04 | Strict CSP with nonces, frame-ancestors none, security headers | XSS and clickjacking | scan: header scan in CI | frontend-engineer | planned | - |
| SEC-AP-05 | CSRF: SameSite cookies + CSRF token | Cross-site request forgery | test: ZAP | backend-engineer | planned | - |
| SEC-AP-06 | SSRF: worker calls allowlisted domains only | Internal network reach | review: egress via proxy/VPC endpoints | cloud-devops-engineer | planned | - |
| SEC-AP-07 | Uploads: magic-byte check, size limit, malware scan, sandboxed parsing, PDF->image; see SEC-AP-07a | Malicious files | test: EICAR + malicious PDF samples | security-engineer | planned | IaC only: `infra/terraform/modules/storage/main.tf` (quarantine bucket, GuardDuty malware protection toggle). Magic-byte check not on main |
| SEC-AP-07a | (new, O-01) Scan-to-promote copies only the exact S3 VersionId that was scanned and verifies its checksum; quarantine denies overwrite after scan | Closes TOCTOU where an object is replaced after scan (U-06) | test: integration replace-after-scan; review: bucket policy | security-engineer | planned | `docs/security/threat-model.md` (U-06) |
| SEC-AP-08 | Rate limits per user/IP/endpoint; daily upload and LLM token quotas | Abuse and denial of wallet | test: k6 | backend-engineer | planned | - |
| SEC-AP-09 | No stack traces; Problem Details with traceId | Avoids information leakage | test: unit | backend-engineer | verified | `apps/api/src/medilens/core/errors.py`; `apps/api/tests/test_errors.py` |
| SEC-AP-10 | CORS limited to app origin | Cross-origin abuse | test: unit | backend-engineer | planned | - |
| SEC-AP-11 | API versioning with deprecation; API inventory | Old endpoints stay protected | scan: OpenAPI diff | backend-engineer | planned | - |

## AI pipeline (SEC-AI)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-AI-01 | OCR text is data, delimited; system prompt forbids following embedded instructions | Indirect prompt injection (LLM01) | test: 50 malicious images | ai-ml-engineer | planned | - |
| SEC-AI-02 | Redact PII (name, phone, ID, address, patient code) before external LLM calls; re-map after | PII to vendor | test: recall >= 99% on labelled set | ai-ml-engineer | implemented | `apps/ai-gateway/src/medilens_ai_gateway/redaction.py`; `apps/ai-gateway/tests/test_gateway.py` (test_redacts_each_pii_class, test_provider_never_sees_raw_pii). Recall not yet measured (O-06) |
| SEC-AI-02a | (new, O-03) If redaction errors for any reason the gateway returns an error and never forwards raw text | Fail-closed default for the PII control (A-02) | test: unit | ai-ml-engineer | verified | `apps/ai-gateway/tests/test_gateway.py` (test_fail_closed_when_redaction_errors) |
| SEC-AI-03 | LLM output must pass JSON Schema validation; never executed or rendered as HTML | Insecure output handling (LLM02) | test: unit | ai-ml-engineer | planned | - |
| SEC-AI-04 | Retrieval filters by profile_id in the retrieval layer | No cross-user leakage in RAG | test: cross-user retrieval | ai-ml-engineer | planned | - |
| SEC-AI-05 | Topic guardrails: block out-of-scope medical advice topics (BR-042); emergencies -> 115 | BR-042 clinical safety | test: 100-question red-team | ai-ml-engineer | planned | - |
| SEC-AI-06 | LLM vendor terms recorded in a Vendor Assessment | Provider retention/training risk | review: document | regulatory-privacy-officer | planned | - |
| SEC-AI-07 | Token limits, timeouts, circuit breakers | Denial of wallet | test: load test | mlops-engineer | implemented | `apps/ai-gateway/tests/test_gateway.py` (test_timeout, test_metering_uses_config_prices); circuit breaker and token caps not yet |
| SEC-AI-08 | Redacted prompt/response logs, 30-day retention | Auditability without PHI | review: Langfuse config | mlops-engineer | planned | - |
| SEC-AI-09 | Model/prompt versions stored; prompt changes via PR + eval | Reproducibility | scan: CI | mlops-engineer | planned | `prompt_version` exists in `apps/ai-gateway/src/medilens_ai_gateway/config.py`; CI eval gate not yet |
| SEC-AI-10 | (new, O-02) Gateway cache key includes tenant, profile scope, prompt version and model; requests without scope are rejected | Key collision would return another user's result (A-09) | test: unit | mlops-engineer | verified | `apps/ai-gateway/tests/test_gateway.py` (test_cache_scoped_by_tenant_and_profile, test_scope_required); `apps/ai-gateway/src/medilens_ai_gateway/gateway.py` |

## Infrastructure (SEC-IN)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-IN-01 | AWS multi-account: management, security/log-archive, dev, staging, prod | Blast-radius isolation | review: account diagram | cloud-devops-engineer | implemented | `infra/terraform/org/main.tf` (not applied) |
| SEC-IN-02 | No root usage; hardware MFA on root; IAM Identity Center | Credential risk | scan: Security Hub | cloud-devops-engineer | implemented | `infra/terraform/org/scp/deny-root.json` |
| SEC-IN-03 | IAM roles, least privilege, no long-lived keys; CI via GitHub OIDC | Key theft | scan: IAM Access Analyzer | cloud-devops-engineer | planned | - |
| SEC-IN-04 | RDS, Redis, workers in private subnets; only ALB public | Network exposure | review: Terraform, Config | cloud-devops-engineer | implemented | `infra/terraform/modules/network`; `infra/terraform/modules/rds-postgres` (not applied) |
| SEC-IN-05 | VPC endpoints for S3, Secrets Manager, KMS, ECR, CloudWatch | Traffic off internet | review: Terraform | cloud-devops-engineer | planned | - |
| SEC-IN-06 | AWS WAF managed rules + rate-based rule | Common web attacks | scan: WAF logs | cloud-devops-engineer | planned | - |
| SEC-IN-07 | Minimal non-root images scanned; no deploy with Critical CVEs | Vulnerable images | scan: CI gate | cloud-devops-engineer | implemented | `.github/workflows/security.yml` (Trivy per app; Inspector not yet) |
| SEC-IN-08 | Secrets in Secrets Manager; DB passwords rotated every 30 days | Secret sprawl | scan: Config rule | cloud-devops-engineer | planned | related: gitleaks in `.github/workflows/ci.yml` |
| SEC-IN-09 | GuardDuty, Security Hub, Config, CloudTrail with Object Lock in every account | Detection and evidence | scan: Security Hub >= 90% | cloud-devops-engineer | planned | related SCP: `infra/terraform/org/scp/deny-disable-security-services.json` |
| SEC-IN-10 | IaC scanning (Checkov/tfsec) in CI; drift detection | Misconfiguration | scan: CI + Config | cloud-devops-engineer | planned | - |

## Logging and incident (SEC-LG)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-LG-01 | Append-only business audit log, kept >= 3 years | Accountability | test: append-only + Object Lock | backend-engineer | implemented | `apps/api/tests/db/test_rls_and_migration.py` (test_audit_is_append_only_and_partitioned); retention/Object Lock not yet |
| SEC-LG-02 | Time sync, UTC ISO-8601 | Forensics | review | sre-operations | planned | - |
| SEC-LG-03 | Alerts: mass failed logins, break-glass, abnormal downloads, IAM changes, CloudTrail off, GuardDuty High | Detection | review: drill | sre-operations | planned | - |
| SEC-LG-04 | Incident Response Plan; 72 h authority notice (Decree 356/2025) | Legal breach duty | review: tabletop every 6 months | security-engineer | planned | - |
| SEC-LG-05 | Forensic evidence preservation | Chain of custody | review: runbook | sre-operations | planned | - |

## Architecture and PHI boundary (SEC-AR)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-AR-01 | Only PHI Service has access to Clinical DB and S3 phi | Boundary of identity data | scan: Access Analyzer + tests | solution-architect | planned | service: `apps/phi-service/src/medilens_phi/service.py`; IAM enforcement not built |
| SEC-AR-02 | Clinical DB holds no email, name or phone; only subject_key | Separates identity from clinical data | test: schema test | data-engineer | verified | `apps/api/tests/db/test_rls_and_migration.py` (test_no_phi_columns_in_clinical_schema) |
| SEC-AR-03 | Worker subnet has no route to NAT/IGW | Exfiltration and SSRF | review: Terraform | cloud-devops-engineer | planned | - |
| SEC-AR-04 | Every LLM call goes through the AI Gateway; IAM denies bedrock:InvokeModel* to others | Single redaction choke point | scan: IAM + test | mlops-engineer | planned | gateway allowlist: `apps/ai-gateway/tests/test_gateway.py` (test_allowlist_rejects_unknown_model); IAM deny not built |
| SEC-AR-05 | Hash-chained audit log with daily integrity check | Tamper evidence | test | backend-engineer | planned | - |
| SEC-AR-06 | Per-record DEK; account deletion by crypto-shredding | Erasure | test | backend-engineer | verified | `apps/phi-service/tests/test_phi.py` (test_crypto_shred_makes_data_unreadable) |
| SEC-AR-07 | Access policies as code (Cedar) with tests for BR-006, BR-030, BR-031 | Reviewable authz | test | backend-engineer | planned | - |
| SEC-AR-08 | DICOM de-identified (PS3.15) before processing (v2) | CT privacy | test | security-engineer | planned | - |
| SEC-AR-09 | Imported PDF/DOCX/ZIP parsed only in sandboxed worker after malware scan | Malicious documents | test: samples | security-engineer | planned | - |

## Legacy short codes (SEC-01..06)
| ID | Statement | Rationale | Verification | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-01 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |
| SEC-02 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |
| SEC-03 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |
| SEC-04 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |
| SEC-05 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |
| SEC-06 | Appears only in docs/plan as early placeholder; superseded by the typed codes above, no separate requirement | Avoid ambiguity | review: remove in next plan revision | security-engineer | planned | `docs/plan/project-plan.en.md` |

## Summary
planned 58, implemented 12, verified 8.
