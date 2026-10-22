# Autopilot (loop operations)

How the autonomous loop runs. **All project-management, source-control and code-quality rules come from [`RULES.md`](../../RULES.md)**; this file only covers loop mechanics.

## Roles
- `medilens-opus-orchestrator` (Opus 5.5, medium): plans, splits, routes, briefs workers, reviews PRs (RULES B4), labels `ready-to-merge`, and updates the state file.
- `medilens-sonnet-worker` (Sonnet 5.5): implements one task on its own branch and worktree, then opens a PR.
- The human owner merges PRs (RULES A3).

## Parallelism and resources
- Default: up to **6 workers in parallel**, only for tasks with disjoint `Paths:`. Spawn the whole batch in one message, each worker with `isolation: "worktree"`.
- Check `free -g` before each batch: available < 6 GB → max 4 workers; < 3 GB → max 2; < 1.5 GB → 1, with no parallel builds.
- Tasks sharing files run sequentially. Dependent tasks stack on the parent PR branch (RULES B1).

## Wake-up cycle
Preflight (`gh auth status`, `git fetch`, `free -g`, state file) → re-review updated PRs → expand the backlog if needed → launch a batch → review the new PRs → update the state file.

## State
- `docs/operations/autopilot-state.md` is updated after every batch and committed on branch `chore/autopilot-state` (one long-lived PR, never pushed to `main`).
- Keep orchestrator context lean: workers report in ≤ 15 lines; use `/compact` on long runs, keeping the state file, the current batch and open PRs.

## Stop conditions
- The time window has elapsed since `Started`.
- No unblocked Sprint 1–2 task remains.
- `gh` is unauthenticated.
- CI or infra fails 3× in a row.
- A data leak is suspected.

On stop, write a handover summary in the state file.
