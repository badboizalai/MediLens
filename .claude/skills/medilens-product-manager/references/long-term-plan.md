# Long-term plan (52 weeks, 26 sprints)

Capacity: 20 h/week (5 days × 4 h). Each sprint = 10 working days; public holidays push later sprints (dates are computed with WORKDAY in the workbook). v1.0 still launches at plan week 32.

| Phase | Sprints | Weeks | Objective | Exit gates | Release |
| --- | --- | --- | --- | --- | --- |
| P0 Initiation & Discovery | S01–S02 | 1–4 | Charter, intended use, user research, MVP scope, golden set v0, OCR choice | G0, G0-R | |
| P1 Foundation | S03–S05 | 5–10 | Repo, CI/CD, landing zone, data model, PHI level A, minimal AI pipeline on staging | G1, G1-D (round 1) | |
| P2 Build MVP | S06–S11 | 11–22 | Upload → OCR → extraction → review, 2D/3D viewer, 3 Units, guarded RAG, timeline, sharing, text input | G2 | |
| P3 Hardening | S12–S14 | 23–28 | Level-B security, performance, a11y, clinical safety, regulatory, external pentest, prod ready | G2-CS, G3, G3-P | |
| P4 Beta & Launch | S15–S16 | 29–32 | Closed beta, UAT, launch, hypercare start | G4 | v1.0 |
| P5 Hypercare & v1.5 | S17–S20 | 33–40 | Digital import, template library, 2 Units, full cascade, donations, annotation | G5-H, G5 | v1.5 |
| P6 v2.0 CT | S21–S26 | 41–52 | CT re-assessment, DICOM de-ID, segmentation, mesh, registration, distillation, FHIR export, closure | G0-R (CT), G1-D (round 2), G6 | v2.0 |

## Sprint goals
S01 initiate (charter, intended use, research) · S02 MVP scope, BRD, prototype, golden v0, OCR bake-off → G0/G0-R · S03 repo, CI, landing zone, VPC, auth · S04 data model, PHI level A, secure upload, design system · S05 minimal AI pipeline + AI Gateway v0 → G1/G1-D · S06 upload + OCR realtime · S07 extraction + Review + cascade v1 · S08 2D viewer + Dental · S09 3D viewer + Cardiology · S10 Oncology + guarded RAG · S11 timeline, text input, sharing, admin, data rights → G2 · S12 level-B security, performance, WCAG · S13 clinical safety, regulatory, summative usability → G2-CS · S14 external pentest, UAT, prod → G3/G3-P · S15 closed beta · S16 launch v1.0 → G4 · S17 hypercare + PDF/DOCX/FHIR import · S18 template library + donations → G5-H · S19 Respiratory + Nephro–Uro Units + full cascade · S20 annotation, data partnership, v1.5 → G5 · S21 CT regulatory re-run + DICOM intake → G0-R (CT) · S22 slice viewer, segmentation, mesh → G1-D round 2 · S23 registration + CT report linking · S24 distillation + cost · S25 FHIR export, v2 hardening, CT validation · S26 v2.0 + year-1 closure → G6.

## Re-plan rules
Use day-10 buffer → cut Should items → reduce Units → move v2.0 to year 2. Never skip gates, security, clinical safety or regulatory work. Log every baseline change in the Change Log sheet first.
