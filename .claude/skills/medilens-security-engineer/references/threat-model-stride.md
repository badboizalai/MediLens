# MediLens Threat Model (seed)

## Data flow and trust boundaries
TB1 Internet ↔ Edge (CloudFront/WAF) · TB2 Edge ↔ VPC (ALB) · TB3 App tier ↔ Data tier (RDS/S3) · TB4 VPC ↔ AWS managed services (Bedrock, SQS via endpoints) · TB5 AWS ↔ external providers (email, any non-AWS AI) · TB6 Prod ↔ non-prod / analytics.

Flows: F1 browser → API (auth, JSON) · F2 browser → S3 (presigned upload) · F3 API → SQS (job IDs) · F4 worker → S3 (read originals) · F5 worker → Bedrock (redacted text/images) · F6 worker → RDS (results) · F7 API → RDS (reads with RLS) · F8 extraction → analytics (pseudonymised) · F9 clinician → API (shared access).

## Seeded threats
| ID | Element | STRIDE | Threat | L | I | Controls | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | F1/API | E, I | IDOR: change document ID to read others' data | 4 | 5 | SEC-AZ-02/03, authz matrix tests | Mitigated when tests pass |
| T02 | F2 | T | Upload malicious file (polyglot PDF, script) | 3 | 4 | SEC-AP-07, GuardDuty Malware Protection for S3, PDF→image | Planned |
| T03 | F5 | I | PHI sent to external model and retained/trained | 3 | 5 | Bedrock VPC endpoint, SEC-AI-02/06 | Planned |
| T04 | F5 | T, E | Prompt injection text in record alters extraction or leaks other data | 4 | 4 | SEC-AI-01/03/04, no tools for LLM | Planned |
| T05 | F9 | S, E | Share link replay after expiry/revoke | 3 | 4 | SEC-AZ-04, signed-in recipients | Planned |
| T06 | Auth | S | Credential stuffing / session theft | 4 | 4 | SEC-ID-02/04/05/06, MFA | Planned |
| T07 | Admin | E, R | Admin browses PHI silently | 2 | 5 | SEC-AZ-05 break-glass + audit | Planned |
| T08 | Logs | I | PHI written to logs / Sentry | 4 | 4 | SEC-DP-06, scrubbers, CI log scan | Planned |
| T09 | F8 | I | Re-identification from analytics | 2 | 4 | DAT-08/09, Lake Formation | Planned |
| T10 | Infra | I | Public S3 bucket / snapshot shared | 2 | 5 | SEC-DP-04, SCPs, Macie, Config | Planned |
| T11 | CI | E | Compromised CI credentials deploy malicious image | 2 | 5 | OIDC with env conditions, signed images, protected branches | Planned |
| T12 | AI | D | Denial of wallet via massive uploads/questions | 3 | 3 | SEC-AP-08, SEC-AI-07 | Planned |
| T13 | Explain | I | LLM reveals other users' data | 2 | 5 | Retrieval scoped in code (SEC-AI-04) | Planned |
| T14 | Repudiation | R | User disputes who viewed shared data | 2 | 3 | Audit log of share access, visible to owner | Planned |

Review this model whenever a new flow, store, provider or role is added.
