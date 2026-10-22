# Architecture Review Checklist

## Structure
- [ ] C4 diagrams match deployed reality
- [ ] Module boundaries enforced (import-linter passes)
- [ ] No module reads another module's tables
- [ ] Unit additions require config + assets only

## Quality attributes
- [ ] Each NFR has a current measurement and is green/amber/red
- [ ] Load test results on staging within targets
- [ ] Failure modes listed for each external dependency with handling

## Decisions
- [ ] All hard-to-reverse choices have ADRs
- [ ] ADRs reviewed for revisit triggers
- [ ] Tech radar updated

## Security & data
- [ ] Threat model current; no High unmitigated
- [ ] Data flows of PHI documented; none leave AWS unredacted
- [ ] Retention and deletion implemented for every store

## Operability
- [ ] Every service has dashboard, alarms, runbook, owner
- [ ] DR drill done in last quarter with RTO/RPO recorded
- [ ] Cost per environment within budget

## Findings format
| # | Finding | Severity (High/Med/Low) | Owner role | Due |
| --- | --- | --- | --- | --- |
