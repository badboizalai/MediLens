# C4 Level 1 - System Context

Status: Draft v0.1 - Owner: solution-architect - Source: plan §8, §16, §24; ADR-0002, ADR-0004.

MediLens helps patients understand their records. It illustrates and explains; it never diagnoses, doses or gives prognosis (BR-042).

```mermaid
C4Context
  title MediLens - System Context
  Person(patient, "Patient / caregiver", "Uploads records, reviews extracted findings, views the body model")
  Person(clinician, "Clinician (shared)", "Views records shared with scope and expiry")
  Person(admin, "Operator / admin", "Runs the platform; break-glass only for PHI")
  System(medilens, "MediLens", "Record upload, OCR + LLM extraction, user review, 2D/3D region viewer")
  System_Ext(idp, "Identity provider", "OIDC login. Cognito or Keycloak (TBD, ADR-003 backlog)")
  System_Ext(llm, "LLM provider", "Amazon Bedrock via VPC endpoint (ADR-0004)")
  System_Ext(ocr, "Cloud OCR (optional)", "Textract for English only, if it beats local OCR on golden set (ADR-0003)")
  System_Ext(email, "Email", "Amazon SES notifications")
  Rel(patient, medilens, "Uses", "HTTPS")
  Rel(clinician, medilens, "Views shares", "HTTPS")
  Rel(admin, medilens, "Operates", "SSM / IAM Identity Center")
  Rel(medilens, idp, "Authenticates users", "OIDC")
  Rel(medilens, llm, "Redacted extraction and explanation prompts", "VPC endpoint")
  Rel(medilens, ocr, "English pages only, if adopted", "VPC endpoint")
  Rel(medilens, email, "Notifications", "TLS")
```

## Trust boundaries at this level
| Boundary | Crossing | Control |
| --- | --- | --- |
| Internet to MediLens | Users, browsers | CloudFront + WAF, TLS, OIDC |
| MediLens to LLM/OCR | Text or images leaving our compute | Only via AI Gateway; PII redaction; in-region VPC endpoint; vendor assessment (SEC-AR-04) |
| MediLens to email | Notification content | No PHI in email bodies (TBD: template review, owner: security-engineer) |

## Open items
| Item | Owner |
| --- | --- |
| Identity provider choice (Cognito vs Keycloak) | solution-architect |
| Textract English adoption | ai-ml-engineer |
| Email content policy | security-engineer |
