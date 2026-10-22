# Business Rules Catalog

Format per rule: code · rule · enforcement point · test idea. Groups: 0xx access, 1xx documents & AI, 2xx display & content, 3xx sharing & data rights.

## 0xx Accounts and access
- **BR-001** Users must be ≥ 18 to self-register; child profiles are created by a guardian and flagged `minor`. · BE (registration), FE (form) · register with birth year < 18 → rejected; caregiver creates minor profile → allowed.
- **BR-002** Terms + health-data processing consent required before first upload; new terms version requires re-consent. · BE middleware on upload endpoints · upload without consent → 403 `/errors/consent-required`.
- **BR-003** MFA mandatory for Clinician and Admin; recommended for Patient; mandatory for Patient when sharing is enabled. · IdP policy + BE check · admin login without MFA → blocked.
- **BR-004** Lock account 15 minutes after 5 consecutive failed logins; email alert. · IdP · 5 bad passwords → locked; 6th correct → still locked until 15 min.
- **BR-005** Session idle timeout 30 minutes; refresh token ≤ 7 days, rotates on use, reuse revokes the chain. · IdP/BE · reuse old refresh token → all sessions revoked.
- **BR-006** RBAC + ownership: a Patient sees only own or shared profiles; Admin cannot read PHI without break-glass (reason, 1 h, alert, audit). · BE service layer + PostgreSQL RLS · user A reads B's doc → 404 + audit.
- **BR-007** Clinician accounts require verification of practice licence before receiving shares (v1.5). · BE + Admin workflow · unverified clinician cannot accept a share.

## 1xx Documents and AI extraction
- **BR-010** Accepted: JPG, PNG, HEIC, PDF; ≤ 20 MB/file; ≤ 30 pages/document. · FE pre-check + BE + worker · 21 MB → 413; .docx → 415.
- **BR-011** Reject image if blur score (variance of Laplacian) < threshold or short side < 1000 px; show re-capture tips. · worker `document.validate` · blurred sample → `rejected` with reason `low_quality`.
- **BR-012** Each field has confidence 0–1; < 0.7 highlighted and must be confirmed. · FE review + BE confirm endpoint · confirm with unconfirmed yellow field → 422 `/errors/unconfirmed-fields`.
- **BR-013** AI output is `draft` until user confirms; only `confirmed` shows on viewer/timeline. · BE query filters · draft finding never returned by `/findings`.
- **BR-014** User edits are versioned (who, old, new, when) and may feed evaluation only with consent. · BE · edit field → history row created.
- **BR-015** Unmappable location → `region = unmapped`, listed separately; never guess. · worker mapping · unknown site text → unmapped.
- **BR-016** Duplicate if same SHA-256, or same visit date + facility + diagnosis → warn, no new record. · BE · re-upload same file → 409 `/errors/duplicate-document`.
- **BR-017** Unit assignment by ICD-10 → Unit table; multi-Unit conditions appear in all; primary Unit defined in table (e.g., lung cancer → Oncology primary, Respiratory secondary). · worker + BE · C34.1 → oncology + respiratory.
- **BR-018** Page classification below confidence 0.6 → page type `unknown`, still OCR'd, flagged in review. · worker · ambiguous page → unknown.
- **BR-019** Extraction cost per document capped (default 0.10 USD); exceeding cap stops LLM steps and asks the user to confirm manual entry. · worker · simulate cap → job ends `needs_manual`.

## 2xx Display and medical content
- **BR-020** Severity palette system-wide: green (monitor), yellow (mild), orange (moderate), red (severe), purple (metastasis/spread); always with icon/text label. · FE tokens · colour-blind simulation still distinguishable via labels.
- **BR-021** Metastasis/spread drawn only when the record states it (M1, "di căn …"); "possible spread" is educational, separate layer, labelled "reference information, not your condition". · FE + BE · record without M1 → no metastasis lines.
- **BR-022** LLM answers only from approved KnowledgeArticles + user's confirmed data; no source → "no information yet, please ask your doctor". · RAG service · question outside KB → fallback answer.
- **BR-023** LLM never gives doses, medication stop/change advice, or survival prognosis; emergency intents → show 115 and urge immediate care. · guardrails · red-team set passes.
- **BR-024** Every KnowledgeArticle has sources, reviewer, review date; > 12 months → flagged for re-review and hidden if > 18 months. · cron `knowledge.review_due` · article reviewed 19 months ago → hidden.
- **BR-025** Pre/post comparison only for same Condition + Region; different units converted (UCUM) or not compared. · BE timeline · mmol/L vs mg/dL converted.
- **BR-026** Every screen showing medical meaning shows the disclaimer "illustration, not a substitute for your doctor". · FE · snapshot test.
- **BR-027** Patient-facing language reading level grade 6–8; medical terms have tooltip definitions. · content review · readability check in QC.

## 3xx Sharing, storage and data rights
- **BR-030** Share scope (all / per Unit / per document), expiry default 7 days, max 90 days, revocable instantly. · BE · expired share → 404.
- **BR-031** Recipient must be signed in; no anonymous public links. · BE · open link logged out → login page.
- **BR-032** Export all data (JSON/PDF); delete account: soft immediately, hard after 30 days (audit logs retained as required). · BE + DE pipeline · deletion request → purge after 30 days verified.
- **BR-033** Originals encrypted; shared previews watermarked with recipient name. · BE/worker · preview contains watermark.
- **BR-034** No model training/fine-tuning on user data without separate opt-in consent. · DE dataset build · dataset excludes non-consented rows.
- **BR-035** Every PHI read/write creates an AuditEvent; append-only; retained ≥ 3 years (configurable). · BE middleware · read finding → audit row.
- **BR-036** Data subject requests acknowledged ≤ 72 h, completed ≤ 30 days. · process + BE · DSR timer.
