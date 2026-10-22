# Delivery Cadence (solo enterprise mode)

## Sprint calendar (2 weeks, ~20 h/week)
| Day | Activity | Hat |
| --- | --- | --- |
| D1 | Sprint planning (1 h), update risk register | PM |
| D1–D9 | Build: alternate hats per block (e.g. Mon BE, Tue FE, Wed AI, Thu QA/DevOps, Fri docs/security) | per story |
| D5 | Backlog refinement (1 h) for next sprint | BA |
| D8 | Security review of the sprint's PRs (1 h) | Security |
| D10 | Review (record 5-min demo), retro (keep/drop/try), evaluation report, status | PM, QC, AI |

## Long-term plan
The day-level plan for all 26 sprints lives in `MediLens_Sprint_Plan_52w.xlsx` (sheets: Dashboard, Settings, Roadmap, Gantt, Sprints, Daily Plan, Gates, Roles, Recurring, Holidays, Change Log). Each day names one main task, the role hat and the skill to call. Day 1 includes planning, day 5 refinement, day 10 review/retro/buffer. Summary in `references/long-term-plan.md`.

## Daily note (5 minutes)
Yesterday · Today · Blockers · Learned.

## Definition of Ready
INVEST story · Gherkin AC · BR/SEC/NFR links · design (if UI) · estimate ≤ 3 days · test data identified · dependencies clear.

## Definition of Done
PR reviewed with Security + QA checklists · tests added, CI green, coverage not lower · AC pass · no High SAST/SCA · logs/metrics/errors in place · authz tested · docs updated · deployed to staging + smoke test · AI changes: golden set not worse than 1 point.

## Delivery metrics to track
- Velocity (points/sprint, rolling 3) and say/do ratio (committed vs done).
- Cycle time per story (start → done).
- Escaped defects per sprint.
- DORA metrics (from DevOps).
- Learning log entries per sprint.

## Retro prompts
- What slowed me down most? Which hat did I avoid?
- Which gate almost failed?
- What would a real team member have caught?
