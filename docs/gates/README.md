# Gates

Phase gates are go/no-go checkpoints. Each gate has a **criterion**, an **owner** who assembles evidence, and a **human approver** who decides. Source of truth: `docs/plan/MediLens_Sprint_Plan_52w.xlsx` (sheet Gates) and the orchestrator handoff protocol (section 5).

## Rule: AI prepares, humans sign
An evidence pack is a **draft for human sign-off**. AI agents never sign a gate, never tick a signature cell and never write a date into it. A gate is passed only when every required human has signed in the pack's sign-off table via a merged PR.

## Process
1. Owner skill builds the pack in `docs/gates/<GATE>.md`: criterion -> evidence link(s) -> status -> gap -> owner.
2. Status vocabulary: `met` (evidence exists and is merged/approved), `partially met` (evidence exists but draft, unmerged or incomplete), `not met` (no evidence). Evidence in an open PR is never better than `partially met`.
3. Reviewers (named in the pack) check evidence against the criterion. Unmerged evidence PRs must be reviewed and merged first.
4. Approvers decide GO / NO-GO / GO with conditions in the sign-off table. Conditions become tracked tasks with an owner and date.
5. The pack is re-issued (new version row) whenever evidence changes. Closed gates are not edited; re-runs get a new pack (e.g. `G0-R-CT`).

## Index
| Gate | Pack | Approver (plan) | Readiness at pack v0.1 |
| --- | --- | --- | --- |
| G0 Discovery Go/No-Go | [G0.md](G0.md) | PM + QC | Not yet ready |
| G0-R Regulatory | [G0-R.md](G0-R.md) | REG | Not yet ready (human REG verification pending) |

Note: the orchestrator handoff table lists steering as G0-R approver, the plan sheet lists REG. Both packs record REG as approver per the plan sheet; PM to confirm whether steering also countersigns.
