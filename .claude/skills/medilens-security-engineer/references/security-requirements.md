# Security Requirements Catalog

Targets: OWASP ASVS 5.0 L2 (application), OWASP Top 10 for LLM (AI), CIS AWS Foundations (infra), Law on Personal Data Protection 91/2025/QH15 + Decree 356/2025/ND-CP (privacy; Decree 356 replaced Decree 13/2023 from 1 Jan 2026).

## Contents
ID identity · AZ authorization · DP data protection · AP application/API · AI LLM · IN infrastructure · LG logging/response · AR architecture (PHI boundary) · SD secure SDLC

## SEC-ID (identity)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-ID-01 | OIDC Authorization Code + PKCE only | MUST | IdP config review, E2E |
| SEC-ID-02 | Password ≥ 12, breached-password check, no forced periodic change | MUST | Unit test |
| SEC-ID-03 | MFA for Clinician/Admin; Patient when sharing | MUST | E2E |
| SEC-ID-04 | Access JWT ≤ 15 min (RS256/ES256), refresh rotation + reuse detection | MUST | Integration |
| SEC-ID-05 | Session cookies HttpOnly, Secure, SameSite; no tokens in localStorage | MUST | Header scan |
| SEC-ID-06 | Lockout after 5 failures, rate limits, CAPTCHA after 3 | MUST | k6 brute-force test |
| SEC-ID-07 | Sign out all devices; active sessions list | SHOULD | E2E |
| SEC-ID-08 | Alerts on new device/country, password/MFA change | SHOULD | E2E |
| SEC-ID-09 | Clinician verification before receiving shares | SHOULD | Workflow |

## SEC-AZ (authorization)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-AZ-01 | Deny by default; every route has a policy | MUST | Route-policy lint fails CI |
| SEC-AZ-02 | Ownership/share check for every ID-based access (anti-IDOR/BOLA) | MUST | Authz matrix tests |
| SEC-AZ-03 | PostgreSQL RLS by profile_id as second layer | MUST | SQL tests as app role |
| SEC-AZ-04 | Share scope + expiry evaluated at access time, cache ≤ 60 s | MUST | Integration |
| SEC-AZ-05 | Admin no PHI; break-glass with reason, 1 h, alert, audit | MUST | E2E + alert test |
| SEC-AZ-06 | Separation of duties for medical content approval | SHOULD | Workflow |
| SEC-AZ-07 | No mass assignment (DTO allowlists) | MUST | Contract tests |

## SEC-DP (data protection)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-DP-01 | TLS 1.2+ everywhere incl. RDS (`rds.force_ssl`), HSTS preload | MUST | SSL Labs, Config |
| SEC-DP-02 | KMS CMK at rest for RDS, S3, EBS, SQS, backups; annual rotation | MUST | Config rules |
| SEC-DP-03 | App-level envelope encryption for identifiers (name, DOB, phone, ID numbers) | MUST | Unit test, DB dump check |
| SEC-DP-04 | S3 Block Public Access (account), TLS-only policy, BucketOwnerEnforced, versioning, Object Lock (audit) | MUST | Config, Access Analyzer |
| SEC-DP-05 | Presigned URLs ≤ 5 min with content-type/size conditions | MUST | Integration |
| SEC-DP-06 | No PHI/PII in logs, traces, error trackers | MUST | Log scan in CI |
| SEC-DP-07 | Synthetic data only outside prod; no snapshot sharing down | MUST | SCP |
| SEC-DP-08 | Crypto-shredding for deletion incl. backups | SHOULD | Runbook test |
| SEC-DP-09 | Watermark shared previews | SHOULD | E2E |

## SEC-AP (application & API)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-AP-01 | Schema validation of all input; reject unknown fields | MUST | Fuzz (schemathesis) |
| SEC-AP-02 | Parameterised queries/ORM only | MUST | Semgrep rule |
| SEC-AP-03 | React escaping; DOMPurify for any HTML | MUST | ESLint rule |
| SEC-AP-04 | Strict CSP with nonce, frame-ancestors none, security headers | MUST | Header scan |
| SEC-AP-05 | CSRF protection for state-changing requests | MUST | ZAP |
| SEC-AP-06 | SSRF prevention: egress allowlist, no user-supplied URLs fetched | MUST | Network policy |
| SEC-AP-07 | Upload: magic bytes, size, malware scan, sandboxed parsing, PDF → image | MUST | EICAR + malicious PDF tests |
| SEC-AP-08 | Rate limits and quotas incl. LLM tokens | MUST | k6 |
| SEC-AP-09 | No stack traces; Problem Details with traceId | MUST | Test |
| SEC-AP-10 | CORS restricted to app origin | MUST | Test |
| SEC-AP-11 | API inventory, versioning, deprecation | SHOULD | OpenAPI diff |

## SEC-AI (LLM)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-AI-01 | Indirect prompt-injection defence: document text is data | MUST | 50 injection images |
| SEC-AI-02 | PII redaction before external LLMs, recall ≥ 99% | MUST | Labelled set |
| SEC-AI-03 | Output schema validation; never execute/render HTML | MUST | Unit tests |
| SEC-AI-04 | Retrieval scoped by profile_id in code | MUST | Cross-user test |
| SEC-AI-05 | Topic guardrails (no dosing/prognosis/diagnosis), emergency routing | MUST | Red-team set |
| SEC-AI-06 | Vendor terms: no training, retention, region documented | MUST | Vendor assessment |
| SEC-AI-07 | Token limits, timeouts, circuit breakers (denial of wallet) | MUST | Load test |
| SEC-AI-08 | Redacted prompt logs, 30-day retention, restricted | SHOULD | Config review |
| SEC-AI-09 | Prompts versioned and reviewed via PR + eval | MUST | CI |

## SEC-IN (infrastructure)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-IN-01 | Multi-account Organizations | MUST before prod | Diagram |
| SEC-IN-02 | No root use; hardware MFA root; Identity Center | MUST | Security Hub |
| SEC-IN-03 | Workload roles least privilege; CI via OIDC | MUST | Access Analyzer |
| SEC-IN-04 | Private subnets for data/compute; minimal SGs | MUST | Terraform review |
| SEC-IN-05 | VPC endpoints for AWS services | SHOULD | Terraform |
| SEC-IN-06 | WAF managed rules + rate rule | MUST | WAF logs |
| SEC-IN-07 | Minimal non-root images, read-only FS, scanned, no Critical CVEs | MUST | CI gate |
| SEC-IN-08 | Secrets Manager with rotation | MUST | Config rule |
| SEC-IN-09 | GuardDuty, Security Hub, Config, CloudTrail org trail everywhere | MUST | Score ≥ 90% |
| SEC-IN-10 | IaC scanning; drift detection; no console changes in prod | MUST | CI + Config |

## SEC-LG (logging & response)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-LG-01 | Business audit log append-only ≥ 3 years | MUST | Object Lock |
| SEC-LG-02 | UTC time sync, ISO-8601 | MUST | Review |
| SEC-LG-03 | Alerts for brute force, break-glass, bulk download, IAM changes, CloudTrail off, GuardDuty High | MUST | Drill |
| SEC-LG-04 | Incident Response Plan with authority/data-subject notification within the legal deadline (72 h from detection under Decree 356/2025, Form 08) | MUST | Tabletop every 6 months |
| SEC-LG-05 | Forensic evidence preservation | SHOULD | Runbook |

## SEC-AR (architecture — PHI boundary, plan section 24)
| Code | Requirement | Strength | Verify |
| --- | --- | --- | --- |
| SEC-AR-01 | Only the PHI Service has IAM/DB access to the clinical DB and `phi` bucket | MUST | IAM Access Analyzer + SQL/IAM tests |
| SEC-AR-02 | Clinical DB holds no email, name or phone; only `subject_key` | MUST | Schema test |
| SEC-AR-03 | Worker subnet has no route to NAT/Internet Gateway | MUST | Terraform test + staging network probe |
| SEC-AR-04 | Every LLM call goes through the AI Gateway; IAM denies `bedrock:InvokeModel*` to all other roles | MUST | IAM policy test |
| SEC-AR-05 | Audit log hash-chained; integrity verified daily | SHOULD | Tamper test |
| SEC-AR-06 | Per-record DEK; account deletion by crypto-shredding | SHOULD (MUST from maturity B) | Deletion test incl. restored backup |
| SEC-AR-07 | Access policies as code (Cedar) with tests for BR-006, BR-030, BR-031 | MUST | Policy unit tests in CI |
| SEC-AR-08 | DICOM de-identified (PS3.15) before any processing; originals only re-downloadable by the owner | MUST (v2) | `dicom_deid_check.py` in CI on test series |
| SEC-AR-09 | Imported PDF/DOCX/ZIP parsed only in the sandboxed worker after malware scan; macros, JS actions, external relationships, zip bombs rejected | MUST | Malicious file test set |

Maturity: A (MVP, synthetic data) → B (before real data / G3-P: separate PHI Service and AI Gateway services and roles, per-record DEK) → C (hospital partners: PHI-vault account, PrivateLink, Verified Permissions, Macie, SIEM).

## SEC-SD (secure SDLC)
Abuse cases per epic · threat model per new data flow · pre-commit secrets scan · SAST/SCA/IaC/container scans with blocking thresholds · SBOM per image · DAST on staging · security sign-off per release · annual (self) pentest against ASVS.
