## Task
- ID: <!-- S1-T03 / BUG-12 -->
- Goal:
- Requirement codes: <!-- BR-/SEC-/NFR- -->
- Owner role (skill): <!-- medilens-backend-engineer -->
- Reviewers: <!-- from routing matrix -->
- Paths: <!-- declared scope -->
- Base / depends on: <!-- main or parent PR # -->

## What & why

## Verification
```
<!-- commands + short output excerpt: make lint, make test, task checks -->
```

## Checklist (RULES.md)
- [ ] Diff stays within declared Paths (B3)
- [ ] Tests added/updated; authz test for any new endpoint (C2, C4)
- [ ] Migration for schema change; ADR for decisions; docs/i18n updated (C2, C6)
- [ ] No secrets, real/realistic patient data, or local tool state (A5)
- [ ] No diagnosis / dosing / prognosis content (BR-042)
- [ ] Conventional Commits, no `--no-verify` (B2)

## Risks / open questions
