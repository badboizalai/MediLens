# Autopilot RULES

Binding for `medilens-opus-orchestrator`, every `medilens-sonnet-worker`, and any session running the autopilot loop. If a rule conflicts with a task, the rule wins and the task is marked **Blocked**.

## R1 — Roles
- **Opus (orchestrator)** plans, splits, routes, reviews PRs, merges, updates state. It does not implement features itself, except for fixes of ≤ 5 lines found during review.
- **Sonnet (workers)** implement exactly one task each, on their own branch and worktree, and open a PR. Workers never merge, never push to `main`, never review their own PR.

## R2 — Parallelism and resources
- Default: **6 workers in parallel**, only for tasks that touch **disjoint paths** (declared in the brief as `Paths:`).
- Before each batch, check `free -g`: available < 6 GB → max 4 workers; < 3 GB → max 2; < 1.5 GB → 1, and do not start builds in parallel.
- Each worker uses `isolation: "worktree"`. No two workers own the same file in the same batch. Tasks that share a file run sequentially.

## R3 — Source-control flow (every task)
1. Branch from up-to-date `main`: `<type>/s<sprint>-<task-id>-<slug>` (e.g. `feat/s1-T03-presign-upload`). Types: feat, fix, test, docs, chore, refactor, ci.
2. Small Conventional Commits; message body ends with the attribution line.
3. `make lint` and `make test` (plus task checks) pass locally **before** pushing.
4. Push the branch and open a PR with `gh pr create`, filling `.github/pull_request_template.md`: task id, requirement codes, owner skill, reviewers, verification evidence.
5. Opus reviews with `gh pr review <n> --comment -b "..."` plus inline comments via `gh api`, **always as real GitHub comments**. Every review ends with a verdict line: `Verdict: READY TO MERGE` or `Verdict: CHANGES REQUESTED`. The review must cover correctness, tests, security/PHI, CLAUDE.md non-negotiables, and scope creep. (GitHub does not allow approving your own PR, and AI does not self-approve.)
6. Changes requested → a worker fixes the same branch, then Opus re-reviews. Max **2 rounds**, after which the task becomes Blocked with a note.
7. **Merging is done by the human owner.** Opus labels the PR `ready-to-merge` (`gh pr edit <n> --add-label ready-to-merge`) and lists it in the state file. A task that depends on an unmerged PR branches from that PR's branch (a stacked PR with `--base <parent-branch>`), and the dependency is noted in the PR body.
8. Never: merge PRs, push to `main`, force-push to shared branches, rewrite published history, `--no-verify`, or disable hooks.

## R4 — What must never be public
- Never commit: `.env*` (except `.env.example`), keys/certs/tokens, `*.pem`, credentials, `~/.git-credentials` content, real or realistic patient data, DICOM, DB dumps, `data/raw`, `ml/datasets/real`, `imaging/dicom-real`, local Claude state (`.claude/settings.local.json`, worktrees), memory exports, logs with PII.
- Fixtures use **synthetic** data only, clearly fake (e.g. `Nguyen Van Test`, birth_year 1900).
- Before every push: `gitleaks protect --staged` (pre-commit) passes, and `git diff --cached --name-only` is checked against the list above.
- A suspected leak → stop the batch, do not push, write a SEV note in the state file, and route it to `medilens-security-engineer`.

## R5 — Quality bar per PR
- New endpoint ⇒ an authz test. Schema change ⇒ an Alembic migration. New decision ⇒ an ADR. UI ⇒ i18n VI/EN keys plus an a11y check.
- No diagnosis, dosing or prognosis content (BR-042).
- Diff stays within the declared `Paths:`; anything else is called out in the PR body.

## R6 — Skills and control layer (use every time)
- Route with `medilens-skill-router`, then work through the owner `medilens-*` skill.
- Apply **karpathy-guidelines** (think first, simplicity, surgical changes, verifiable goals) and **ponytail** (smallest working solution) to every task.
- Use **mattpocock-skills**: `/tdd` for logic and `/grill-with-docs` when a task is ambiguous (Opus answers from the docs; unresolved questions become Blocked).
- Use **taste-skill** for any `apps/web` UI, and **laya** MCP (`laya_route` / `laya_decide`) for quick typed classification when routing is ambiguous.

## R7 — Memory and context
- **claude-mem** captures sessions automatically. Wrap anything sensitive in `<private>…</private>`.
- The single source of truth for progress is `docs/operations/autopilot-state.md`, updated after every batch: task table (id, branch, PR #, status, owner skill), decisions, blockers, time used.
- Durable decisions go into an ADR or `docs/agents/project-context.md`, not only memory.
- Keep the orchestrator context lean: workers return ≤ 15-line reports; on long runs use `/compact`, keeping the state file path, the current batch and open PRs.

## R8 — Stop conditions
Stop when any of these holds: 12 hours since `Started`; no remaining unblocked Sprint 1–2 tasks; `gh` unauthenticated; repeated CI or infra failure (3×); suspected data leak. Write a handover summary in the state file on stop.
