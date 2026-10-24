# MediLens Business Rules Catalog (BR-001 … BR-051)

Source of truth: `docs/plan/project-plan.en.md` (§4.1–4.4 for BR-001…035, §26.5 for BR-040…045). Rule text is condensed from the plan; wording changes go through a change request. Owner = role accountable for enforcing the rule. Test idea = one line, to be expanded into TC-xxx by QA. Synthetic data only.

Release column: **MVP** = v1.0 (Dental, Cardiology, Oncology), **v2** = text/digital/CT inputs (plan §26).

## 0xx Accounts and access (plan §4.1)
| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-001 | Self-registration requires age ≥ 18; child profiles are created only by a guardian (Caregiver) and flagged `minor`. | Backend Engineer | §4.1 | Register with birth year making user 17 → rejected; Caregiver creates minor profile → allowed and flagged. | MVP |
| BR-002 | Terms + health-data processing consent must be accepted before first upload; a new terms version requires re-consent. | Regulatory/Privacy Officer | §4.1 | Upload without consent → 403 `/errors/consent-required`; bump terms version → upload blocked until re-consent. | MVP |
| BR-003 | MFA mandatory for Clinician and Admin; recommended for Patient. | Security Engineer | §4.1 | Admin login without second factor → denied; Patient login without MFA → allowed with prompt. | MVP |
| BR-004 | Lock account 15 min after 5 consecutive failed logins; send email alert. | Security Engineer | §4.1 | 5 wrong passwords then correct one → still locked; email alert sent; unlocked after 15 min. | MVP |
| BR-005 | Session expires after 30 min inactivity; refresh token ≤ 7 days and rotates on each use. | Security Engineer | §4.1 | Idle 31 min → 401; reuse an already-rotated refresh token → rejected. | MVP |
| BR-006 | RBAC + ownership (ABAC): Patient sees only own or shared profiles; Admin sees no medical content without a logged reason (break-glass). | Backend Engineer | §4.1 | User A requests user B's document → 404/403 + audit; Admin reads PHI without reason → denied. | MVP |

## 1xx Documents and AI extraction (plan §4.2)
| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-010 | Accepted formats JPG, PNG, HEIC, PDF; ≤ 20 MB/file; ≤ 30 pages/document. | Backend Engineer | §4.2 | 21 MB file → 413 `/errors/file-too-large`; `.docx` → rejected; 31-page PDF → rejected. | MVP |
| BR-011 | Reject images with blur score (Laplacian variance) below threshold or short side < 1000 px; show re-capture guidance. | AI/ML Engineer | §4.2 | Blurred synthetic photo → 422 `/errors/low-quality-image` with tips; 500 px image → rejected. | MVP |
| BR-012 | Every extracted field has confidence 0–1; fields < 0.7 are highlighted yellow and must be confirmed by the user. | AI/ML Engineer | §4.2 | Confirm with an unconfirmed yellow field → 422 `/errors/unconfirmed-fields`; 0.69 flagged, 0.70 not. | MVP |
| BR-013 | AI results stay `draft` until the user confirms → `confirmed`; only `confirmed` data appears on viewer and timeline. | Backend Engineer | §4.2 | Draft finding never returned by `/findings`; appears after confirmation. | MVP |
| BR-014 | User edits are versioned (who, old/new value) and used for model evaluation (with consent). | Data Engineer | §4.2 | Edit a field → history row (user, old, new); evaluation set excludes users without consent. | MVP |
| BR-015 | If a finding cannot be mapped to a body region, set `region = unmapped` and list it; never guess a location. | Clinical Informaticist | §4.2, §27.2 | Unknown site text → `unmapped` and listed; mapping confidence < 0.6 → `unmapped`. | MVP |
| BR-016 | Duplicate if same file hash, or same visit date + facility + diagnosis → warning, no new record. | Backend Engineer | §4.2 | Re-upload same file → 409 `/errors/duplicate-document`; same date/facility/diagnosis → duplicate warning. | MVP |
| BR-017 | Unit classification via ICD-10 → Unit mapping table; multi-Unit conditions appear in all, Oncology primary (e.g. lung cancer → Oncology + Respiratory). | Clinical Informaticist | §4.2 | C34.1 → Oncology (primary) and Respiratory; MVP shows only enabled Units. | MVP |

## 2xx Display and medical content (plan §4.3)
| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-020 | One severity palette: green (monitor), yellow (mild), orange (moderate), red (severe), purple (metastasis/spread); always with symbol/text label. | UX/UI Designer | §4.3 | Colour-blind simulation: each level still distinguishable by label; no colour-only indicator. | MVP |
| BR-021 | Metastasis shown only when the record states it (M1, "liver metastasis"); "possible spread" is separate educational content labelled "reference information, not your condition". | Clinical Safety Officer | §4.3 | Record without M1 → no metastasis lines; "possible spread" layer carries the label. | MVP |
| BR-022 | LLM answers only from approved KnowledgeArticles (RAG) + user's own data; no source → "no information yet, please ask your doctor". | AI/ML Engineer | §4.3 | Question outside the KB → fallback answer; every answer carries citations. | MVP |
| BR-023 | LLM never gives doses, never advises stopping/changing medication, never predicts survival; emergency questions → show 115 and urge immediate care. | Clinical Safety Officer | §4.3 | Red-team prompts ("how many mg", "how long do I have") refused; "chest pain" → 115 first. | MVP |
| BR-024 | KnowledgeArticle needs sources (WHO, MoH, NIH/MedlinePlus, guidelines), reviewer, review date; flagged for re-review after 12 months. | Clinical Safety Officer | §4.3, §9.2 | Article last reviewed 13 months ago appears in `knowledge.review_due`; article without source cannot publish. | MVP |
| BR-025 | Pre/post comparison only between BodyFindings of same Region and Condition; different units → convert or do not compare. | Clinical Informaticist | §4.3 | mmol/L vs mg/dL glucose converted; different region → no comparison offered. | MVP |

## 3xx Sharing, storage and data rights (plan §4.4)
| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-030 | Share scope (all / per Unit / per document); expiry default 7 days, max 90; revocable instantly. | Backend Engineer | §4.4 | 91-day expiry → rejected; revoke → recipient gets 404 immediately; out-of-scope document hidden. | MVP |
| BR-031 | Share links work only for signed-in recipients; no anonymous public links. | Security Engineer | §4.4 | Open link while signed out → login required, no data leaked. | MVP |
| BR-032 | Users can export all data (JSON/PDF) and request account deletion: soft delete immediately, hard delete after 30 days (audit logs retained as required). | Data Engineer | §4.4 | Export contains all user data; deletion request → purged from every store at day 30, audit retained. | MVP |
| BR-033 | Originals stored encrypted; shared previews watermarked with recipient's name. | Security Engineer | §4.4 | Object has KMS encryption; preview image shows recipient name. | MVP |
| BR-034 | No model training/fine-tuning on user data without separate opt-in consent. | Regulatory/Privacy Officer | §4.4 | Dataset build excludes non-opted-in users; consent withdrawal removes rows. | MVP |
| BR-035 | Every read/write of medical data creates an AuditEvent; logs append-only, kept ≥ 3 years (configurable). | Security Engineer | §4.4 | Read a finding → audit row; attempt to update/delete audit row → denied. | MVP |

## 4xx Multi-source input and imaging (plan §26.5)
| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-040 | A `patient_reported` finding gets no ICD-10 code and no severity colour; always labelled "you described". | Clinical Safety Officer | §26.5 | Free-text entry → no ICD-10, neutral colour, label shown. | v2 |
| BR-041 | A text description with emergency signs shows 115 before any other content (like BR-023). | Clinical Safety Officer | §26.5 | Text "đau ngực dữ dội" → 115 banner rendered before all content. | v2 |
| BR-042 | CT images only build illustrative anatomy; no automatic detection or measurement of lesions (stays outside SaMD scope). Also a v1 non-goal. | Regulatory/Privacy Officer | §26.5, §22.2 | Pipeline emits anatomy meshes only; no lesion/measurement output field exists; claims review passes. | v2 (constraint applies from v1) |
| BR-043 | DICOM de-identified before any processing step; only the user can re-download the original. | Medical Imaging Engineer | §26.5 | Synthetic DICOM with PHI tags → none remain downstream; other user cannot fetch original. | v2 |
| BR-044 | Conflicting sources: `record` > `image_derived` > `patient_reported`, with a mismatch warning. | Clinical Informaticist | §26.5 | Record says right kidney, patient text says left → record wins, mismatch warning shown. | v2 |
| BR-045 | Text-layer digital records extracted directly without OCR; valid FHIR mapped without the LLM. | AI/ML Engineer | §26.5 | Text-layer PDF → no OCR job; valid FHIR Bundle → zero LLM calls. | v2 |

## 4xx Oncology content (draft — pending CSO (D99), task S10-T91)
Drafts proposed by the BA for Clinical Safety Officer agreement. **Not approved**; do not implement as final until the CSO signs off (D99). Extends BR-020, BR-021, BR-023, BR-024, BR-041, BR-042. Source column "R16" = plan risk R16; "§FE" = plan frontend/sensitive-content notes (FE-VW-05, calm summary + "Show details").

| ID | Rule | Owner role | Source | Test idea | Release |
| --- | --- | --- | --- | --- | --- |
| BR-046 | Oncology records open in summary mode by default (calm summary, no metastasis layer, no per-region detail). Detail, including the metastasis layer, appears only after an explicit tap on "Show details"; the choice is not remembered silently across records. | UX/UI Designer | R16, §FE | Open synthetic oncology record → summary only, no `is_metastasis` marker rendered; tap "Show details" → detail panel. | MVP |
| BR-047 | MediLens never shows or generates survival, prognosis or stage-to-outcome statements (no percentages, years, "good/poor outlook"). A question asking for them gets a refusal that points to the care team. Extends BR-023, BR-042. | Clinical Safety Officer | R16, BR-023, BR-042 | Red-team prompts ("5-year survival of stage III?") refused in VI and EN; golden-set output scan finds no outcome figures. | MVP |
| BR-048 | TNM (and stage/grade) is shown verbatim as written in the record. Next to it, a plain-language note explains what each letter means in general (T = tumour extent, N = lymph nodes, M = distant spread) — never what the value means for this patient. | Clinical Informaticist | R16, BR-021 | Record "T2N0M0" → shown as "T2N0M0" with letter explanations; no sentence interpreting the value for the user. | MVP |
| BR-049 | Metastasis lines and markers use a neutral style: no alarm colour, flashing or animation; always paired with a text label naming the site and "stated in your record". They follow BR-021 (only when the record states it) and BR-020 (never colour alone). | UX/UI Designer | R16, BR-020, BR-021, FE-VW-05 | Render M1 synthetic record → marker has a text label and no animation; record without M → no marker. | MVP |
| BR-050 | Oncology wording is calm and non-alarmist, offers "ask your care team" prompts with each detail section, and shows support/mental-health links. Emergency signs described in text or questions show 115 first (BR-023, BR-041). | Clinical Safety Officer | R16, BR-023, BR-041 | Oncology detail panel contains a care-team prompt and support link; text "ho ra máu nhiều" → 115 banner before other content. | MVP |
| BR-051 | Every oncology KnowledgeArticle needs a CSO review date in addition to BR-024 (sources, reviewer, 12-month re-review); an article without a CSO review date is not retrievable by RAG. | Clinical Safety Officer | BR-024, R16 | Ingest oncology article without CSO review date → rejected; with date → retrievable; date older than 12 months → flagged. | MVP |

### Open questions for CSO (not guessed)
1. Exact wording of the VI/EN reassurance and refusal copy (examples in `docs/requirements/stories/oncology.feature.md` are illustrative).
2. Is general stage definition text ("stage III") allowed, or only TNM letters? Draft allows only letters.
3. Should "Show details" be re-confirmed per session or per record? Draft: per record.
4. Which support/mental-health links are approved for Vietnam?
5. Does CSO review of oncology KnowledgeArticles use the same 12-month cycle as BR-024?

## Gaps (TBD ids)
The plan defines no rule for these ids. They are listed so numbering gaps are explicit; do not implement until a change request adds them.

| ID | Status | Note |
| --- | --- | --- |
| BR-0TBD-0xx-a (007–009) | TBD | Unassigned in the 0xx group (the BA skill reference catalog has a Clinician-licence rule that is not in the plan). |
| BR-0TBD-1xx-a (018–019) | TBD | Unassigned in the 1xx group (the BA skill reference catalog has page-classification fallback and per-document cost cap; not in the plan). |
| BR-0TBD-2xx-a (026–029) | TBD | Unassigned in the 2xx group (a disclaimer on every screen is a plan principle in §1 and mitigation of R01 in §11, but has no BR id; candidate for a change request). |
| BR-0TBD-3xx-a (036–039) | TBD | Unassigned in the 3xx group (data-subject-request timelines appear in the BA skill reference catalog only; plan §13.10 covers DSR duties). |
