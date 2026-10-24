# DSR store inventory (S11-T106)

Every place personal data lives, how it is exported and erased. Update this table in the same PR as any new store (a store missing here is a DSR bug).

| Store | Data | Export | Erase | Timeline |
|---|---|---|---|---|
| `identity.users`, `patient_profiles`, `consents` | account, profiles (incl. soft-deleted), consents | `GET /v1/me/export` | `identity.erase_user()` (SECURITY DEFINER), hard delete | same request |
| `clinical.documents`, `document_pages`, `extraction_runs`, `extraction_fields` | document metadata, OCR fields, confirmed values | export (metadata + confirmed fields) | `SqlDocumentDsr` / `SqlExtractionDsr` hard delete | same request |
| `clinical.encounters`, `conditions`, `body_findings`, `observations` | clinical facts incl. `patient_reported` | export | `SqlClinicalDsr` hard delete | same request |
| `clinical.knowledge_chunks` | per-profile embeddings and text | not exported (derived) | `SqlKnowledgeDsr` delete | same request |
| `clinical.share_grants` | shares given and received | export | deleted by profile and by grantee | same request |
| `clinical.outbox` | events carrying profile/document ids | not exported | deleted by `payload.profile_id` | same request |
| `worker.document_status` | job status per document | not exported | `SqlDocumentDsr` delete | same request |
| S3 `quarantine/{profile}/`, `raw/{doc}/`, `pre/{doc}/`, `ocr/{doc}/`, `extractions/{doc}/` | original files, derived images, OCR text | presigned URL (15 min) for originals | `DsrStorage.delete_prefix` | same request |
| `audit.audit_events` | who did what (ids only) | not exported | **not deleted**: legal retention; `actor_id` pseudonymised (`md5(receipt salt || id)`) | same request; events kept per audit retention |
| `audit.break_glass_grants` | support access grants | not exported | deleted | same request |
| `audit.erasure_receipts` | receipt id + hash of IdP subject | n/a | kept as proof of erasure (no PII) | audit retention |
| Backups / snapshots | copies of all of the above | n/a | not rewritten; expire by retention (RDS 35 days) | at most one backup cycle after erasure |

`verify_erased(user)` (DsrService) checks every row above plus S3 prefixes; only pseudonymised audit may remain. Failure rolls the transaction back (S3 deletes are idempotent, so a retry completes them). Withdrawal of consent only sets `withdrawn_at` and stops processing; it deletes nothing.
