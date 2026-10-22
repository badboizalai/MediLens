# ADR-0001: Monorepo with in-repo Claude skills and router agent

- Status: Accepted · Date: 2026-10-22
- Context: One-person "enterprise" team; apps, assets, infra, safety/regulatory records and 23 role skills must evolve together.
- Decision: Single monorepo (uv + pnpm workspaces). Skills live in `.claude/skills/`, versioned with code; one `medilens-skill-router` agent selects skills; `medilens-orchestrator` handles multi-role flows.
- Alternatives: polyrepo (rejected: overhead for one person); skills in `~/.claude` (rejected: not versioned/shared).
- Consequences: CI validates skills; shared context synced by script; skills changed only via PR.
