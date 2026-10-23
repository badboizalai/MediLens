# Architecture Decision Records

File numbers are sequential; the plan ID (plan §16.3) is kept in each title.

| File | Plan ID | Title | Status |
| --- | --- | --- | --- |
| [0001](0001-monorepo-and-skill-pack.md) | n/a | Monorepo with in-repo Claude skills and router agent | Accepted |
| [0002](0002-modular-monolith.md) | ADR-001 | Modular monolith with an AI worker | Proposed |
| [0003](0003-hybrid-ocr.md) | ADR-006 | Hybrid OCR (local + cloud/LLM vision baseline) | Proposed |
| [0004](0004-region-and-bedrock.md) | ADR-012 | AWS region and Bedrock model availability | Proposed |
| [0005](0005-worker-api-handoff.md) | n/a (S6-T53) | Worker to API hand-off of document status and extraction results | Proposed |

Template: `.claude/skills/medilens-solution-architect/assets/adr-template.md`. `VERIFY:` marks facts to check before acceptance.
