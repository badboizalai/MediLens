# MediLens RULES — project management & code quality

Binding for every contributor: humans, Claude sessions, sub-agents. When a rule conflicts with a task, the rule wins, and the task is raised as blocked with the reason. Changing these rules requires a PR labelled `rules`, merged by the owner.

---

## Part A — Project management

### A1. Work items
- Every change starts from a task with an id (`S<sprint>-T<nn>`, `BUG-<n>`, `CHORE-<n>`), a goal, an owner role (skill), reviewers, requirement codes (BR-/SEC-/NFR-/DAT-…), acceptance criteria, `Paths:` in scope, and a sprint/gate.
- **Definition of Ready**: acceptance criteria are testable, dependencies are known, no open question blocks the work, and the size is ≤ 1 day (split it otherwise).
- **Definition of Done**: code + tests + docs are updated; CI is green; the PR is reviewed and merged; the acceptance criteria are demonstrated; the tracker is updated; nothing from A5 is violated.

### A2. Planning and tracking
- The sprint scope comes from `docs/plan/` (§5.1 and the 52-week sheet). Changing scope mid-sprint requires a change note in the tracker, and a CR (`medilens-business-analyst`) if it touches a signed-off requirement.
- The single tracker for delivery status is `docs/operations/autopilot-state.md` (task table: id, owner, branch, PR, status, base, blockers). GitHub PRs and issues mirror it.
- Statuses: `todo → in-progress → in-review → changes-requested → ready-to-merge → done`, plus `blocked`.
- Risks go into the risk register (`medilens-product-manager`). Decisions that are hard to reverse get an ADR in `docs/architecture/adr/`.

### A3. Roles and ownership
- Each folder has one owner role (`docs/architecture/repository-structure.md`, `.github/CODEOWNERS`). The routing matrix (`medilens-orchestrator/references/routing-matrix.md`) names the reviewers.
- Authors never merge their own work. The reviewer merges.
- **AI merge (authorised by the owner on 2026-10-23):** the Opus orchestrator may merge a PR written by a Sonnet worker only when all of these hold: its own review verdict is `READY TO MERGE`; all review threads are resolved; local checks or CI are green; the PR touches no `RULES.md`, `.claude/settings*.json` or `.github/workflows/` (those always need the human owner); and no human gate is implied. Otherwise the human owner merges. The owner can revoke this at any time.
- Human gates (clinical safety G2-CS, regulatory G0-R, data licence G1-D, pentest G3-P, release GO/NO-GO) cannot be signed by an AI; the AI prepares the evidence only.

### A4. Communication and records
- Discussion about code lives in the PR. Decisions are recorded where they last: ADR, `project-context.md`, or the requirements docs. Chat or memory alone is not enough.
- Reply in Vietnamese by default. Code, identifiers, commits and PR titles are in English.

### A5. Data protection and what must never be public
- **Never committed, pushed, logged or put into a prompt:** `.env*` (except `.env.example`), keys/certs/tokens, credentials, real or realistic patient data, DICOM, DB dumps, the contents of `data/raw`, `ml/datasets/real`, `imaging/dicom-real`, local tool state (`.claude/settings.local.json`, worktrees, memory exports), and logs containing PII.
- Fixtures and examples use **obviously synthetic** data (e.g. `Nguyen Van Test`, birth_year 1900).
- gitleaks (pre-commit + CI) must pass. Before pushing, review `git diff --cached --name-only`.
- A suspected leak means: stop, do not push, do not "fix" it by rewriting public history yourself; raise SEV and route to `medilens-security-engineer`.
- Product content never contains diagnosis, dosing, medication changes or prognosis (BR-042).

---

## Part B — Source control

### B1. Branches
- `main` is protected: no direct pushes, no force-pushes. Every change goes through a PR.
- Branch name: `<type>/<task-id>-<slug>`, e.g. `feat/S1-T03-presign-upload`. Types: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`, `ci`, `perf`.
- One task per branch. Branch from up-to-date `origin/main`, or from the parent PR's branch when the work depends on an unmerged PR (a stacked PR, with `--base` set to the parent and the dependency stated in the PR body).

### B2. Commits
- Conventional Commits: `type(scope): imperative summary` (≤ 72 chars). The body explains *why*. Scopes: `web`, `api`, `worker`, `ai-gateway`, `phi`, `assets`, `ml`, `data`, `infra`, `docs`, `skills`.
- Keep commits small and buildable. No `--no-verify`, no disabling hooks, no committing generated junk or lockfile churn unrelated to the task.

### B3. Pull requests
- Keep PRs small: aim for < 400 changed lines excluding generated files. Larger work is split into stacked PRs.
- Fill in `.github/pull_request_template.md`: task id, requirement codes, owner role, reviewers, `Paths:`, verification evidence (commands + output excerpt), risks, and screenshots for UI.
- The diff stays within the declared `Paths:`; anything outside is explained or removed.
- Merge requires: at least one review addressing B4 by someone other than the author (the human owner, or the Opus orchestrator under A3), a green CI (or posted local evidence when CI is unavailable), an up-to-date branch, and resolved conversations. Merge method: squash, then delete the branch.

### B4. Code review checklist (every review covers all of these)
1. **Correctness**: logic, edge cases, error paths, and concurrency/idempotency where relevant.
2. **Tests**: they exist at the right level, test behaviour rather than implementation, and would fail without the change.
3. **Security & privacy**: authz on every endpoint (IDOR), input validation, no PHI in logs or prompts, secrets handling, dependency risk.
4. **Architecture**: module boundaries (import-linter), dependency direction, `region_code` contract, no cross-module table access.
5. **Simplicity**: the smallest working solution, no speculative abstraction, no dead code.
6. **Scope**: only the task; no drive-by refactors.
7. **Docs**: OpenAPI/README/ADR/i18n are updated when behaviour changes.
- Reviews are posted as real PR comments, with inline comments on specific lines and a final verdict: `READY TO MERGE` or `CHANGES REQUESTED`. Two failed rounds escalate the task to `blocked` with a note.

---

## Part C — Code quality

### C1. General
- Readable over clever. Match the surrounding style. Functions do one thing. Names are domain words from the glossary.
- No commented-out code, no `print` debugging, no TODO without a task id (`TODO(S2-T07): …`).
- Errors are explicit: fail fast at the boundaries, and never swallow exceptions silently.
- Configuration comes from the environment via typed settings. Never hard-code URLs, secrets or magic numbers without a named constant.

### C2. Python (`apps/*`, `ml/`, `tools/`)
- Python **3.10**. Type hints are required on public functions; run `mypy --strict` for the `domain` and `application` layers.
- `ruff check` + `ruff format` are clean. Use `structlog`, never `print`, and never log PHI.
- Hexagonal modules: `api → application → domain`; `infra` implements domain ports. Modules communicate via application services or domain events only.
- DB: SQLAlchemy 2. Every schema change ships an Alembic migration (reversible where possible). Tables use UUIDv7 PKs, `created_at`/`updated_at`, soft delete, and RLS by `profile_id`.
- API: errors are RFC 9457 Problem Details; endpoints are versioned under `/v1`; cursor pagination; idempotency keys on unsafe retries; every endpoint has an authz dependency **and** an authz test.

### C3. TypeScript / web (`apps/web`, `packages/*`)
- `strict` TypeScript, no `any` without a justification comment; ESLint and Prettier are clean.
- Server state uses TanStack Query, UI state uses Zustand, forms use React Hook Form + Zod. Components in `components/ui` contain no business logic.
- Every user-visible string goes through i18n with VI and EN keys; no hard-coded copy.
- Accessibility follows WCAG 2.2 AA: labels, keyboard access, contrast, and an axe check in tests.
- Viewer assets: mesh and SVG ids equal `region_code`, validated by the asset check scripts.

### C4. Testing
- The test pyramid: unit (fast, many) → integration (Testcontainers) → contract/API → E2E (Playwright, critical flows only) → load (k6, before release gates).
- A new behaviour gets a test that fails first (TDD for domain logic). A bug fix starts with a regression test.
- Coverage target: ≥ 70% overall, ≥ 85% for `domain`. Coverage is a floor, not a goal.
- Tests are deterministic: no real network, no real time (inject a clock), no shared state, and synthetic data only. Flaky tests are fixed or quarantined with a task id within one sprint.

### C5. Dependencies and infrastructure
- Add a dependency only with a reason in the PR (licence, maintenance, size). Pin versions; Dependabot updates them.
- Terraform: `fmt` + `validate` clean, modules versioned, every resource tagged, no `apply` from a laptop to shared environments (CI only, with approval).
- Containers run as non-root, use a pinned base image, and must pass a Trivy scan.

### C6. Documentation
- Public behaviour changes update the README, OpenAPI or user docs in the same PR.
- An architectural decision gets an ADR (template in `medilens-solution-architect/assets/adr-template.md`).
- Runbooks accompany anything that needs operating (`docs/runbooks/`).

---

## Part D — AI-assisted work
- Route first (`medilens-skill-router`), then work through the owner `medilens-*` skill.
- Always apply **karpathy-guidelines** (think first, simplicity, surgical changes, verifiable goals) and **ponytail** (smallest working solution). Use **mattpocock-skills** `/tdd` for logic and `/grill-with-docs` when a task is ambiguous. Use **taste-skill** for UI, and **laya** for quick typed routing or classification.
- AI output follows every rule above. Claims of "done" must include verification evidence.
- Memory: claude-mem is automatic. Wrap sensitive text in `<private>`. Durable facts belong in repo docs, not only in memory.
