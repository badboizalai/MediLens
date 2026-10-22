# Backend PR Checklist

## Must (block if missing)
- [ ] Every endpoint/use case with a resource ID performs an ownership/share check (test included)
- [ ] No PHI/PII in logs, metrics, traces, errors, URLs, queue payloads
- [ ] Input validated with DTO; extra fields rejected; output DTO excludes internal fields
- [ ] Errors are Problem Details with correct type; no stack traces
- [ ] DB writes + outbox in one transaction; consumers idempotent
- [ ] Migration is backward compatible (expand/contract); downgrade tested
- [ ] OpenAPI updated; breaking changes versioned
- [ ] Tests added (unit + integration + authz); coverage not lower
- [ ] Secrets via Secrets Manager; no new long-lived credentials

## Should
- [ ] Metrics/trace attributes for new paths
- [ ] Indexes for new query patterns; `EXPLAIN` reviewed for queries > 50 ms
- [ ] Docs (README/ADR) updated
- [ ] Rule functions named after BR codes
