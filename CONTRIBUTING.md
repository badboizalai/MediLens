# Contributing
1. Pick/open an issue (template: owner role, reviewers, requirement codes, sprint/gate).
2. Branch `feat|fix|docs|chore/<scope>-<short>`; Conventional Commits (`feat(api): ...`).
3. Route with `/route` to find owner + reviewers; follow the owner skill's workflow.
4. `make lint test` must pass; new endpoint ⇒ authz test; schema change ⇒ Alembic migration; decision ⇒ ADR.
5. PR with the template checklist; reviewers = those named by the routing matrix; release gates RG-01…RG-21 via `medilens-qc-release-gatekeeper`.
6. Changing a skill: edit `.claude/skills/...`, bump `metadata.version`, run `make skills-check`. Shared context: edit `docs/agents/project-context.md` then `make skills-sync`.
