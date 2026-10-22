# Post-market Surveillance

## Intake
Support tags any ticket mentioning wrong medical information, confusion about a diagnosis, distress, emergency or harm with `safety=yes` and routes it to the CSO (support skill escalation matrix).

## Triage (within 1 working day)
| Class | Example | Default action |
| --- | --- | --- |
| A — potential serious harm | Emergency text not routed; dosing advice shown | Immediate mitigation (feature flag off, guardrail patch), incident record, notify PM/QC |
| B — misleading information | Wrong side, wrong organ, outdated article | Fix within the sprint; hazard-log update |
| C — confusion/distress without misinformation | User frightened by oncology view | UX/content change; trend |
| D — not safety-related | Login problem | Back to support |

## Records
`assets/safety-incident-report-template.md`; hazard-log update (new hazard or adjusted probability); monthly trend table (count by class, Unit, input type); quarterly review in the steering report.

## CAPA
Corrective and preventive action for class A/B: root cause, correction, prevention (test, rule, design change), effectiveness check date.
