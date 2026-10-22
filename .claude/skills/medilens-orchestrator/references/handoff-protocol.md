# Hand-off Protocol

## 1. Hand-off packet (always)
Use `assets/handoff-packet-template.md`. Minimum fields: from-role, to-role, objective, inputs (links, files, codes), decisions already made (ADR ids), constraints (SEC/NFR codes), definition of done, known risks, open questions.

## 2. Entry / exit criteria per role
| Role skill | Entry criteria (can start when…) | Exit criteria (done when…) |
| --- | --- | --- |
| business-analyst | Feature brief with problem + metric | Stories INVEST, Gherkin AC, BR links, glossary updated |
| product-manager | Inputs from BA/QA/SRE | Prioritised backlog, sprint goal, risks updated |
| ux-ui-designer | Stories + AC | All states designed (loading/empty/error/success), copy in VI/EN, a11y notes, tokens used |
| solution-architect | Requirements + NFRs | ADR accepted, C4 updated, NFRs measurable |
| ai-ml-engineer | Schema fields agreed with BA, eval set exists | Eval report vs baseline, Model/Prompt Card, guardrails tested |
| data-engineer | Schema/contract from BE | Catalog entry, DQ tests, lineage, retention set |
| backend-engineer | AC + design + threat model delta | Code + tests + OpenAPI + migration, PR checklist passed |
| frontend-engineer | Design spec + API contract | Code + tests + Storybook, budgets met, a11y 0 serious |
| cloud-devops-engineer | ADR (if new service) + security requirements | IaC merged, plan reviewed, deployed to staging, runbook |
| security-engineer | Design or PR | Findings with severity, sign-off or blockers listed |
| qa-engineer | AC available | Tests written + automated, results reported |
| qc-release-gatekeeper | Build on staging + test results | GO/NO-GO report with evidence |
| sre-operations | Feature in staging | SLO/alerts/runbook exist; for incidents: postmortem done |
| clinical-safety-officer | Feature/Unit/input description + screens or outputs | Hazard-log delta, CS requirements with verification, review record (approved/changes/rejected) |
| regulatory-privacy-officer | Intended use + feature/data/provider description | RDR or "no change" note, DPIA/OTIA impact, claims decision |
| clinical-informaticist | Unit brief or input sample | Region tree, code mappings, FHIR/import spec, format checks PASS |
| data-curator | Data need (component, labels, size) | License Register decision, Dataset Card, leakage check PASS, agreement report if labelled |
| mlops-engineer | Model/prompt candidate with eval results | Registry entry, Model Card, router config, cost model, promotion record |
| medical-imaging-engineer | RDR allowing CT scope + licensed test data | De-ID PASS, meshes within budget, TRE report, QC checklist |
| 3d-medical-artist | Region list for the Unit | GLB/SVG within budgets, names = region_code, licences + attribution |
| technical-writer | Final UI strings / feature behaviour | VI/EN docs and strings, i18n_check PASS, CSO review for medical strings |
| support-success | Release notes + known issues | Macros, KB articles, support model ready; hypercare report during G5-H |

## 3. RACI for recurring decisions
R = responsible, A = accountable, C = consulted, I = informed.
| Decision | PM | BA | UX | SA | AI | DE | BE | FE | DevOps | Sec | QA | QC | SRE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MVP scope | A | R | C | C | C | I | C | C | I | C | C | I | I |
| Business rule | C | A/R | C | I | C | I | C | I | I | C | C | I | I |
| Architecture/ADR | C | I | I | A/R | C | C | C | C | C | C | I | I | C |
| AI model change | I | C | I | C | A/R | C | I | I | C | C | C | I | C |
| Data retention | C | C | I | C | I | R | R | I | I | A | I | I | C |
| Release GO/NO-GO | A | I | I | C | C | I | C | C | C | C | C | R | C |
| Incident command | I | I | I | C | C | C | C | C | C | C | I | I | A/R |
| Security sign-off | I | I | I | C | C | C | C | C | C | A/R | C | C | I |

### RACI for Part III decisions
| Decision | CSO | Reg/Priv | Clin. Inf. | Data Curator | MLOps | Imaging | 3D Artist | Writer | Support | PM | QC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Publish medical content | A | C | C | I | I | I | I | R | I | I | C |
| Anatomical region mapping | A | I | R | C | I | C | R | I | I | I | I |
| Use a dataset for training | C | A | C | R | C | C | I | I | I | I | I |
| Change model/provider | C | C | I | C | R | I | I | I | I | A | C |
| Add CT input | A | A | C | C | C | R | C | I | I | C | C |
| Release (clinical safety evidence) | R | C | I | I | I | I | I | I | I | A | R |
| Leave hypercare (G5-H) | C | I | I | I | I | I | I | I | R | A | R |

## 4. Escalation
- Gate fails twice on the same item → escalate to product-manager to re-plan scope.
- Any SEC MUST that cannot be met → security-engineer records risk acceptance (who, why, until when) or blocks.
- Any safety concern in medical content → clinical-safety-officer records it in the hazard log; qc-release-gatekeeper blocks release until resolved.
- Any feature or claim beyond the intended use → regulatory-privacy-officer blocks until a new RDR exists.
- Any dataset without a licence decision → data-curator blocks its use; no exceptions for "just testing".

## 5. Phase gates (owner → approver)
| Gate | Sprint | Owner skill | Approver |
| --- | --- | --- | --- |
| G0 Discovery | S02 | product-manager | qc-release-gatekeeper |
| G0-R Regulatory (and CT re-run at S21) | S02 / S21 | regulatory-privacy-officer | steering (+ external advice when needed) |
| G1 Architecture ready | S05 | solution-architect | qc-release-gatekeeper |
| G1-D Data licence (round 2 at S22) | S05 / S22 | data-curator | regulatory-privacy-officer |
| G2 Feature complete | S11 | product-manager | qc-release-gatekeeper |
| G2-CS Clinical safety | S13 | clinical-safety-officer | real clinician signature |
| G3 Release gate v1.0 (RG-01…21) | S14 | qc-release-gatekeeper | product-manager |
| G3-P External pentest | S14 | security-engineer | independent tester report |
| G4 Launch review | S16 | product-manager | steering |
| G5-H Hypercare exit | S18 | support-success + sre-operations | qc-release-gatekeeper |
| G5 Release v1.5 | S20 | qc-release-gatekeeper | product-manager |
| G6 Release v2.0 + closure | S26 | qc-release-gatekeeper | steering |
