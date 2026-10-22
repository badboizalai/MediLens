# Secure Review Checklists

## Design
- [ ] Data flows and classes identified; trust boundaries crossed listed
- [ ] Threat model delta done; Highs mitigated
- [ ] Least data: only fields needed; retention defined
- [ ] Consent/purpose covered for new processing

## Backend PR
- [ ] Ownership/share check on every ID access; 404 on denial; audit written
- [ ] Input validation, no raw SQL, no `eval`/`pickle` on untrusted data
- [ ] No PHI/PII in logs/errors/traces/queue payloads
- [ ] Secrets from Secrets Manager; no new credentials in code/config
- [ ] File handling: type/size checks, temp files in /tmp, cleaned
- [ ] External calls via allowlisted adapters with timeouts

## Frontend PR
- [ ] No `dangerouslySetInnerHTML` without DOMPurify; LLM output as safe markdown
- [ ] No tokens in JS storage; no PHI in URLs/analytics/Sentry
- [ ] CSP not weakened; no new third-party script origins

## Terraform
- [ ] No public access except ALB/CloudFront; SG rules minimal
- [ ] Encryption with correct CMK; logging enabled
- [ ] IAM: no `*` on PHI resources; conditions where possible
- [ ] Deletion protection/backups on data stores (prod)
- [ ] Checkov clean or justified skips

## Prompt / AI change
- [ ] Document text delimited and declared untrusted
- [ ] Output schema enforced; no tool use beyond JSON
- [ ] Redaction applied before external calls
- [ ] Red-team set passes; no regression in false-block rate
