# MediLens

Web app that helps patients **understand** their medical records: upload (photo/PDF/digital/text) → OCR + LLM extraction → user review → 2D/3D body viewer coloured by region. It **illustrates and explains; it never diagnoses, doses or gives prognosis** (BR-042).

## Start here
- Product/architecture context: `docs/agents/project-context.md`
- Full plan: `docs/plan/project-plan.vi.md` (VI) / `project-plan.en.md`; schedule `docs/plan/MediLens_Sprint_Plan_52w.xlsx`
- Repo structure: `docs/architecture/repository-structure.md`
- Skills (23 roles) live in `.claude/skills/`; catalog in `docs/agents/skill-catalog.md`

## How to work: route first
For any non-trivial task, use the **`medilens-skill-router`** agent (or `/route <task>`) to pick the owner skill and reviewers, then invoke it (`/medilens-<role>`). Multi-role work → `medilens-orchestrator`.

## AI control layer (always on)
Installed plugins/tools — use them in every session and tell sub-agents to use them:
- **andrej-karpathy-skills** — think before coding, simplicity first, surgical changes, verifiable goals.
- **ponytail** — smallest solution that works (YAGNI, stdlib first).
- **mattpocock-skills** — `/grill-with-docs` before non-trivial changes, `/tdd` for logic, issue/spec flows.
- **taste-skill** — any UI/frontend work (`apps/web`, design-system).
- **claude-mem** — cross-session memory (local, Anthropic plan; cloud sync off). Wrap sensitive text in `<private>`.
- **laya** (MCP, if enabled) — fast typed routing/classification decisions.
- **WebMCP** — web app exposes page tools via `navigator.modelContext` (`apps/web/src/lib/webmcp/`).
Autonomous delivery: `medilens-opus-orchestrator` (Opus) delegates to parallel `medilens-sonnet-worker` (Sonnet) agents; **binding rules in `docs/operations/autopilot-rules.md`** (branch + PR per task, real GitHub review comments, human merges, no secrets/real data); state in `docs/operations/autopilot-state.md`.

## Layout (monorepo)
`apps/{web,api,worker,phi-service,ai-gateway}` · `packages/{anatomy-assets,api-client,design-system}` · `ml/` · `imaging/` · `data/` · `infra/` · `regulatory/` · `safety/` · `docs/` · `tests/` · `tools/`

## Commands
`make help` lists everything. Common: `make up` (local stack), `make api-dev`, `make web-dev`, `make lint`, `make test`, `make skills-check`.

## Non-negotiables
- No real patient data in repo, dev/staging, logs, tests, fixtures or un-redacted prompts. `data/raw`, `ml/datasets/real`, `imaging/dicom-real` are gitignored and denied to Claude.
- Authorization on every endpoint + a test for it (`backend-engineer/assets/test-authz-template.py`).
- Modules talk only via `application` services/domain events (import-linter in CI).
- Region codes (`region_code`) are the contract between data, API, GLB/SVG assets and viewer.
- Skills are process-as-code: change via PR, bump `metadata.version`, edit `docs/agents/project-context.md` then `python3 tools/sync_skill_context.py`.
- Reply to the user in Vietnamese by default; code, identifiers and commits in English.
