# Routing Matrix

Owner = produces the deliverable. Reviewers = must check before done. Use the request type column to search.

## Contents
1. Product & requirements
2. Design
3. Architecture
4. AI / ML
5. Data
6. Backend
7. Frontend
8. Cloud / DevOps
9. Security & compliance
10. Quality
11. Operations
12. Clinical safety and regulatory
13. Data sourcing and annotation
14. Terminology and interoperability
15. MLOps and AI cost
16. Imaging and 3D assets
17. Documentation and support
18. Ambiguous phrasings

## 1. Product & requirements
| # | Problem / request | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 1 | "Write the BRD/SRS/PRD" | business-analyst | product-manager | BRD/SRS document |
| 2 | Turn an idea into user stories | business-analyst | qa-engineer | Stories + Gherkin AC |
| 3 | A business rule is unclear or conflicts | business-analyst | product-manager, security-engineer (if access/data) | Updated BR catalog entry |
| 4 | Medical term or abbreviation meaning | business-analyst | ai-ml-engineer | Glossary entry |
| 5 | Which features go in MVP | product-manager | business-analyst | MoSCoW list |
| 6 | Plan the next sprint | product-manager | all owners of selected stories | Sprint plan |
| 7 | We are behind schedule | product-manager | solution-architect | Re-plan with scope cuts |
| 8 | Weekly status / risk review | product-manager | — | Status report, risk register |
| 9 | Should we release? | qc-release-gatekeeper | product-manager, security-engineer | Readiness report GO/NO-GO |
| 10 | Change request after sign-off | business-analyst | product-manager | CR form + impact |

## 2. Design
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 11 | Design a new screen/flow | ux-ui-designer | business-analyst, frontend-engineer | Design spec |
| 12 | Colours/typography/tokens | ux-ui-designer | frontend-engineer | tokens.json |
| 13 | Content feels scary (cancer, metastasis) | ux-ui-designer | qc-release-gatekeeper | Revised copy + layout |
| 14 | Accessibility of a design | ux-ui-designer | qa-engineer | A11y review |
| 15 | Run a usability test | ux-ui-designer | product-manager | Test plan + report |
| 16 | How a Unit viewer should look (teeth, heart) | ux-ui-designer | frontend-engineer, ai-ml-engineer | Unit visual spec |

## 3. Architecture
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 17 | Monolith vs microservices | solution-architect | cloud-devops-engineer | ADR |
| 18 | Choose identity provider / DB / queue | solution-architect | security-engineer | ADR |
| 19 | Define NFRs | solution-architect | sre-operations, qa-engineer | NFR catalog |
| 20 | Integration with an external system | solution-architect | security-engineer | Integration spec + ADR |
| 21 | Draw C4 diagrams | solution-architect | — | C4 Mermaid/Structurizr |
| 22 | Architecture review at phase end | solution-architect | all | Review record |
| 23 | How to make adding a Unit config-only | solution-architect | backend-engineer, frontend-engineer | Design + ADR |

## 4. AI / ML
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 24 | OCR accuracy is low | ai-ml-engineer | qa-engineer | Error analysis + fix |
| 25 | Handwriting is unreadable | ai-ml-engineer | ux-ui-designer (fallback UX) | Pipeline change |
| 26 | Write/refine the extraction prompt or JSON Schema | ai-ml-engineer | business-analyst | Prompt + schema version |
| 27 | Map text location to region_code | ai-ml-engineer | frontend-engineer | Mapping rules |
| 28 | Build the RAG explain feature | ai-ml-engineer | security-engineer, business-analyst | RAG design + guardrails |
| 29 | LLM is hallucinating | ai-ml-engineer | qa-engineer | Eval + mitigation |
| 30 | Create synthetic records | ai-ml-engineer | data-engineer | Generator + dataset card |
| 31 | Evaluate a new model/provider | ai-ml-engineer | solution-architect, security-engineer | Eval report + ADR |
| 32 | Prompt injection inside an uploaded image | security-engineer | ai-ml-engineer | Test set + fix |
| 33 | Train a CV model (teeth, skin) | ai-ml-engineer | data-engineer | Model card |
| 34 | AI cost too high | ai-ml-engineer | cloud-devops-engineer | Cost plan |

## 5. Data
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 35 | Design tables for a new feature | backend-engineer | data-engineer | Migration + ERD update |
| 36 | Classify data / update catalog | data-engineer | security-engineer | Catalog entry |
| 37 | Build analytics pipeline / dashboard | data-engineer | product-manager | dbt models + dashboard |
| 38 | Data quality issue | data-engineer | backend-engineer | DQ rule + fix |
| 39 | Retention / deletion policy | data-engineer | security-engineer | Retention matrix |
| 40 | User asks to delete their data | data-engineer (pipeline) | security-engineer (approval), backend-engineer | DSR completion record |
| 41 | Load ICD-10/LOINC catalog | data-engineer | ai-ml-engineer | Versioned reference load |
| 42 | Event contract for analytics | data-engineer | backend-engineer | Data contract YAML |

## 6. Backend
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 43 | Implement endpoint X | backend-engineer | security-engineer, qa-engineer | Code + tests + OpenAPI |
| 44 | User can see another user's data (IDOR) | security-engineer (incident) → backend-engineer (fix) | qa-engineer | Fix + regression test |
| 45 | Job stuck / DLQ growing | sre-operations | backend-engineer | Incident + fix |
| 46 | Slow endpoint | backend-engineer | sre-operations | Profiling + fix |
| 47 | Schema migration | backend-engineer | data-engineer | Alembic migration |
| 48 | Add a worker job | backend-engineer | ai-ml-engineer | Job + tests |

## 7. Frontend
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 49 | Build page/component | frontend-engineer | ux-ui-designer | Code + Storybook + tests |
| 50 | 3D model too heavy / low FPS | frontend-engineer | — | Optimised asset + perf report |
| 51 | Mesh names do not match region_code | frontend-engineer | ai-ml-engineer | Fixed asset + CI check |
| 52 | New Unit viewer plugin | frontend-engineer | ux-ui-designer | Plugin |
| 53 | Lighthouse/Web Vitals regression | frontend-engineer | sre-operations | Fix |
| 54 | CSP/XSS issue | security-engineer → frontend-engineer | qa-engineer | Fix |

## 8. Cloud / DevOps
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 55 | Which AWS service for X | cloud-devops-engineer | solution-architect | Recommendation (+ADR if hard to reverse) |
| 56 | Write Terraform for X | cloud-devops-engineer | security-engineer | Module + plan output |
| 57 | CI/CD pipeline | cloud-devops-engineer | security-engineer, qa-engineer | Workflow YAML |
| 58 | Deploy / rollback | cloud-devops-engineer | sre-operations | Deploy record |
| 59 | Cloud bill spiked | cloud-devops-engineer | sre-operations | Cost analysis |
| 60 | New environment | cloud-devops-engineer | security-engineer | Terraform + runbook |

## 9. Security & compliance
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 61 | Threat model a feature | security-engineer | solution-architect | STRIDE model |
| 62 | Security review a PR/design | security-engineer | — | Review findings |
| 63 | PDPL 91/2025 / Decree 356/2025 compliance | security-engineer | business-analyst | Checklist + DPIA |
| 64 | Vulnerability found (CVE, report) | security-engineer | cloud-devops-engineer | Vuln record + fix plan |
| 65 | Suspected data breach | security-engineer | sre-operations, product-manager | Incident response |
| 66 | Vendor assessment (LLM/OCR) | security-engineer | solution-architect | Vendor assessment |

## 10. Quality
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 67 | Test strategy/plan | qa-engineer | product-manager | Strategy + plan |
| 68 | Write test cases for a story | qa-engineer | business-analyst | Test cases |
| 69 | Automate E2E / API / load tests | qa-engineer | frontend/backend-engineer | Test code |
| 70 | Flaky tests | qa-engineer | owner of code | Root cause + fix |
| 71 | Exploratory testing session | qc-release-gatekeeper | — | Session notes + bugs |
| 72 | Medical content review | qc-release-gatekeeper | business-analyst | Review record |

## 11. Operations
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 73 | Define SLOs/alerts | sre-operations | solution-architect | SLO doc + alarms |
| 74 | Site is down / errors spike | sre-operations | cloud-devops-engineer | Incident + postmortem |
| 75 | Write a runbook | sre-operations | owner of system | Runbook |
| 76 | DR drill | sre-operations | security-engineer | Drill record |
| 77 | Model drift in production | sre-operations (detect) → ai-ml-engineer (fix) | qa-engineer | Drift report + action |
| 78 | Monthly maintenance | sre-operations | all | Maintenance report |

## 12. Clinical safety and regulatory
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 79 | Is MediLens (or feature X) a medical device? | regulatory-privacy-officer | clinical-safety-officer | RDR (G0-R) |
| 80 | Write the intended use | regulatory-privacy-officer | product-manager | Intended Use Statement |
| 81 | Build/update the hazard log | clinical-safety-officer | qa-engineer | Hazard log + CS requirements |
| 82 | Sign the Clinical Safety Case before beta | clinical-safety-officer | qc-release-gatekeeper | CSC (G2-CS) |
| 83 | Review how a finding/organ/implant is displayed | clinical-safety-officer | ux-ui-designer, 3d-medical-artist | Clinical review record |
| 84 | Clinical validation with doctors | clinical-safety-officer | data-curator | VAL report |
| 85 | Privacy notice, consent texts | regulatory-privacy-officer | technical-writer, ux-ui-designer | Notice + consent texts |
| 86 | DPIA / overseas transfer assessment | regulatory-privacy-officer | security-engineer, data-engineer | DPIA/OTIA dossiers |
| 87 | Marketing or UI wording might over-claim | regulatory-privacy-officer | technical-writer | Claims review record |
| 88 | New model/use case risk | regulatory-privacy-officer | mlops-engineer, clinical-safety-officer | AI impact assessment |

## 13. Data sourcing and annotation
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 89 | Where can we get data for X? | data-curator | ai-ml-engineer | Sourcing plan |
| 90 | Can we use dataset Y (licence, DUA)? | data-curator | regulatory-privacy-officer | License Register entry |
| 91 | How many samples are enough? | data-curator | ai-ml-engineer | Sizing note (sample_size.py) |
| 92 | Label data / hire annotators | data-curator | clinical-safety-officer | Guideline + agreement report |
| 93 | Users want to donate data / withdraw consent | data-curator | regulatory-privacy-officer, data-engineer | Donation record / exclusion |
| 94 | Hospital data partnership | regulatory-privacy-officer | data-curator, security-engineer | DSA + DPIA/OTIA |

## 14. Terminology and interoperability
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 95 | Map terms to ICD-10/LOINC; SNOMED licence | clinical-informaticist | ai-ml-engineer | Mapping table / decision |
| 96 | Region tree, laterality, precision for a Unit | clinical-informaticist | 3d-medical-artist, clinical-safety-officer | Region config |
| 97 | Import PDF/DOCX/FHIR | clinical-informaticist | backend-engineer, security-engineer | Import spec + checks |
| 98 | Export FHIR | clinical-informaticist | backend-engineer | Export spec + validator run |

## 15. MLOps and AI cost
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 99 | Token cost too high / which model per task | mlops-engineer | ai-ml-engineer | Cost model + routing change |
| 100 | Set escalation thresholds | mlops-engineer | ai-ml-engineer | threshold_tuner report |
| 101 | Roll out a new model/provider | mlops-engineer | ai-ml-engineer, security-engineer, regulatory-privacy-officer | Promotion checklist |
| 102 | Self-host or API? GPU serving | mlops-engineer | cloud-devops-engineer | Break-even + ADR |

## 16. Imaging and 3D assets
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 103 | Accept CT uploads safely | medical-imaging-engineer | security-engineer | Intake + de-ID pipeline |
| 104 | Organ meshes from CT; align to template | medical-imaging-engineer | 3d-medical-artist, clinical-safety-officer | Mesh + TRE report |
| 105 | New organ model / model too heavy | 3d-medical-artist | frontend-engineer | GLB + budget report |
| 106 | Template by sex/age; resected organ; implant glyph | 3d-medical-artist | clinical-safety-officer, frontend-engineer | Template/glyph assets |

## 17. Documentation and support
| # | Problem | Owner | Reviewers | Deliverable |
| --- | --- | --- | --- | --- |
| 107 | User guide / capture guide / FAQ | technical-writer | ux-ui-designer | Docs VI/EN |
| 108 | Translate or check i18n files | technical-writer | clinical-safety-officer (medical strings) | i18n_check PASS |
| 109 | Release notes | technical-writer | product-manager, regulatory-privacy-officer | Notes VI/EN |
| 110 | Users report problems / support setup | support-success | product-manager | Support model + macros |
| 111 | User says a finding is wrong or asks for medical advice | support-success | clinical-safety-officer | Reply + safety record |
| 112 | Are we ready to leave hypercare? | support-success | sre-operations, qc-release-gatekeeper | G5-H decision |

## 18. Ambiguous phrasings
| User says | Interpret as | Route |
| --- | --- | --- |
| "Làm sao cho nhanh hơn" | Latency (API) or FPS (viewer) or pipeline time — ask which if unclear | backend / frontend / ai-ml |
| "Bảo mật cái này" | Threat model + review | security-engineer |
| "Lên kế hoạch" | Roadmap/sprint (PM) unless technical design (architect) | product-manager |
| "Kiểm tra giúp" | Test (QA) for code; release check (QC) for a build | qa / qc |
| "Dữ liệu sai" | Extraction wrong (AI) vs stored wrong (BE) vs report wrong (DE) | ask for an example, then route |
| "Deploy" | cloud-devops-engineer; if in prod incident, sre-operations | — |
| "Có hợp pháp không / có được không" | Device question → regulatory; data licence → data-curator; privacy → regulatory + security | regulatory-privacy-officer |
| "Có an toàn cho bệnh nhân không" | Clinical safety (not security) unless about data leaks | clinical-safety-officer |
| "Chi phí AI / tốn token" | Token/GPU cost → MLOps; cloud bill → DevOps | mlops-engineer |
| "Mô hình 3D" | Asset → 3D artist; viewer code → frontend; CT-derived → imaging | 3d-medical-artist |
| "Người dùng phàn nàn" | Support triage first; safety flag → CSO | support-success |
