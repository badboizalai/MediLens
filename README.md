# MediLens

Web app that helps patients **understand** their own medical records — upload → OCR + LLM extraction → review → 2D/3D body viewer coloured by region. It illustrates and explains; it never diagnoses, doses, or prognoses.

- Plan: [`docs/plan/`](docs/plan) · Architecture: [`docs/architecture/repository-structure.md`](docs/architecture/repository-structure.md) · Context: [`docs/agents/project-context.md`](docs/agents/project-context.md)

## Quick start
```bash
make setup      # .env, uv sync, pnpm install, pre-commit
make up         # postgres+pgvector, redis, minio, keycloak, mailpit
make migrate
make api-dev    # http://localhost:8000/docs
make web-dev    # http://localhost:3000
make help
```
Requires: Docker, Python 3.12 + [uv](https://docs.astral.sh/uv/), Node 20 + pnpm 9.

## Working with Claude Code
Open the folder in VS Code (accept recommended extensions). Claude reads `CLAUDE.md`, the 23 skills in `.claude/skills/`, and the `medilens-skill-router` agent. Try `/route "OCR đọc sai số răng trong ảnh mờ"` or `/medilens-backend-engineer ...`. See [`docs/agents/skill-pack-readme.md`](docs/agents/skill-pack-readme.md).

## Repo map
See [`docs/architecture/repository-structure.md`](docs/architecture/repository-structure.md).

> Safety: no real patient data in dev/staging/logs/tests/prompts. Legal/regulatory content is for learning, not legal advice.
