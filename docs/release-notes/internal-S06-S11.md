# Internal release notes: increment S06-S11

Task S11-T109 (D109) · internal only, not for users · Source: merged PRs on `origin/main` up to #128 and the repo files they changed. Grouped by the sprint number in each task id (BUG and CHORE items are listed under the sprint of the area they fix). Nothing here is a sign-off; hazard rows, articles and BR drafts below are still drafts.

## S06: upload, pipeline, processing screen
- Upload API and safety: malicious-file test set (#69), upload review vs SEC-AP-07 (#77), polyglot/evasion hardening (#79), rejected uploads marked `rejected` (#78), pixel cap and OCR worker image (#89).
- Pipeline: job/event JSON Schemas (#71), ADR-0005 (#65, accepted in #85) and ADR-0006 RLS definer functions (#85), api-events queue and IAM (#68), chained steps with status events (#73), export of results and `extraction.completed` (#82), consumer applying document status (#84), ingest of `extraction.completed` (#106), status SSE stream (#102).
- Worker: edge detection and perspective warp (#74), rules page classifier (#76), classify to pick the Unit (#86), 9-type synthetic set and classifier eval (#90), SSE-KMS writes with PHI CMK (#87), storage wiring in staging (#81).
- Web: processing progress screen with retake guidance (#99).
- Fixes: BUG-01 401/403 (#62), BUG-02 status GET and upload cap (#61), BUG-03 (#60), BUG-04 (#63), BUG-05 (#67, #70), BUG-06 confirm gate returns 422 with `field_ids` (#88), BUG-08 terminal guard (#92), BUG-09 (#103), BUG-10 red-team misses (#121), BUG-11 pgvector test image (#123).

## S07: review, extraction, normalising
- API review endpoints with ownership and audit (#72), review screen with confirm gate BR-012 (#75), source page image with bbox highlight (#122).
- Extraction prompt v2 with few-shots and line-anchored citations (#110), terminology normaliser with abbreviations and a LOINC subset (#115), anatomy region mapping with FDI and laterality rules (#83) and mapping of extracted findings (#98).
- AI Gateway cascade with confidence escalation and USD metering (#94).
- Hazard log v1 draft (#80). Pipeline metrics mart with daily data-quality checks (#126).

## S08: viewer 2D, Units, evaluation data
- 2D body SVG with `region_code` ids (#66), 2D body viewer with severity colours and region list (#93), FDI odontogram SVG (#95) and odontogram viewer component (#105).
- Dental and cardiology Unit configs with LOINC subset (#100), dental VI-EN terminology with licence-gated ICD-10 (#91).
- 600-document synthetic golden set per Unit with stratified eval harness (#118).
- Confirmed extraction projected into clinical findings (#112). Viewer state spec and D79 review kit (#127).

## S09: 3D, performance, security headers
- Body and heart GLB with `region_code` meshes (#104), 3D viewer with region picking (#109), 3D performance budget with automatic 2D fallback (#114).
- CSP, security headers and CORS allow-list (#113).

## S10: knowledge, safety, oncology
- Safety guardrails for medicine-amount, outlook, condition-naming and emergency questions (#101), red-team gate (#119) and its fixes (#121).
- Semantic cache and per-user token quota in the gateway (#108).
- Knowledge RAG with pgvector and profile-scoped retrieval (#120). 20 draft KnowledgeArticles VI/EN (#111).
- Oncology content rules and Gherkin (#107).

## S11: timeline, sharing, admin
- Timeline comparing two visits and profile body page (#117).
- Patient-reported findings with location NER, API only (#125).
- Time-limited sharing with Cedar policies (#124); share screen and watermarked clinician view (#128).
- Admin without PHI and audited break-glass (#116).

## What users can reach today (web routes)
`/[locale]/upload`, `documents/[id]/progress`, `documents/[id]/review`, `profiles/[id]/body`, `profiles/[id]/timeline`, `profiles/[id]/sharing`, `shared/[shareId]`, plus sign-in and the dashboard (the dashboard links only to upload; other pages are opened by URL). No route exists for the odontogram, patient-reported input, RAG explanations, or data export/delete. No export or delete endpoint was found on main. The user guide (`docs/user-guide/user-guide.*.md`) marks these as "coming soon" or "not available".

## Known limitations
- GLB models are procedural placeholders, not real anatomy; real asset pending licence review (`packages/anatomy-assets/README.md`).
- Safety guardrails are regex rules, no classifier (`guardrails.py`, shortcut note); misses found by the red-team set were patched case by case (#121).
- Gateway semantic cache is token-set Jaccard with a linear scan, not embeddings, and cache and quota state are held in process memory, so they reset on restart and are not shared between instances.
- No model F1 on real or independent data yet: classifier score uses a synthetic set from the same templates and is not G2 evidence (autopilot state). Golden set is synthetic.
- Gateway prices per 1K tokens are assumptions.
- Dental term wording, 20 KnowledgeArticles, hazard log v1 rows and BR-046..BR-051 are drafts pending the Clinical Safety Officer.
- ICD-10 codes stay unloaded until licence LIC-002 is cleared (G1-D).
- Oncology summary-mode default (BR-046) and related drafts are not implemented in the web app.
- Sharing screen takes a recipient user ID (UUID), not an email.

## Ops actions required
1. Grant `api_events_consumer` to the consumer login (ADR-0006) and run migrations through the latest.
2. Terraform apply for staging: AWS credentials, remote state, `kms_admin_role_arns`, staging reviewers; point `var.worker_image` at the worker image built with the OCR extra.
3. Provide pgvector in the database used by knowledge retrieval.
4. Decide a shared store for gateway cache and quota before running more than one instance.
5. Workflow files changed by CI PRs are merged by a human.

## Human gates open
- G2-CS: CSO review of `draft-pending-CSO` hazard rows, dental term wording, KnowledgeArticles and BR-046..BR-051.
- G0 / G0-R sign-off (human) and G1-D (LIC-002 before any ICD-10 code is loaded).
- Consent form lines 6 and 27 wording (claims lint decision, regulatory owner).
- Review of the user guide drafts (VI/EN) by CSO and regulatory owner before publication.
