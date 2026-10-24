# Upload malicious file set (S6-T57)

Tests: `apps/api/tests/document/test_malicious_uploads.py`; payloads are built in code by `malicious.py` (no binaries committed). Refs: SEC-AP-07, threat model U-02/U-05, abuse case AC-02.

| Payload | Blocking layer | Test |
|---|---|---|
| EICAR renamed .pdf / .jpg | API magic bytes (415); GuardDuty is the AV layer for real malware | `test_eicar_renamed_is_rejected` |
| PNG bytes declared `application/pdf` | API declared == sniffed (415) | `test_declared_pdf_but_png_bytes_is_rejected` |
| HTML/script with no magic bytes | API magic bytes (415) | `test_html_without_magic_is_rejected` |
| Empty file | API: size 0 at presign (400); empty object at complete (415) | `test_empty_declared_size_is_400`, `test_empty_object_is_rejected` |
| Object > 20 MB | API size check (413) | `test_oversize_object_is_413_and_removed` |
| PDF with `/JavaScript` + `/OpenAction` | worker validate `pdf_active_content` (BUG-05b, #67; byte-level, defence in depth); API accepts | `test_content_level_payloads_pass_api_and_are_left_to_worker`; also hex-escaped names, `/AA`, `/OpenAction`, `pdf_uninspectable` for `/ObjStm`/`/Encrypt` (S6-T58-F3) |
| JPEG+ZIP polyglot | worker validate decodes and re-encodes to PNG, dropping the appended ZIP (S6-T58-F4; sandboxed decode still open, F4b); API accepts | `test_jpeg_zip_polyglot_is_stripped`, `test_image_with_trailing_html_is_stripped` (BUG-14: only re-encoded output is stored) |
| `%PDF-` header followed by HTML/script | worker validate `pdf_malformed` (needs `%%EOF` near the end and `startxref`/`/Root`; S6-T58-F4); full PDF-to-image in a sandbox is F4b; API accepts. BUG-14: also `trailing_data` (>16 bytes after last `%%EOF`) and `pdf_polyglot` (`PK\x03\x04`, `<html`, `<script`, `<!doctype html` anywhere; rare false positive on binary streams accepted) | `test_rejections` |

Rejected uploads: Problem Details type/status asserted, quarantine object deleted, no outbox row.

Known gap: a rejected document stays `uploaded-pending` (no `rejected` status) - `test_rejected_document_status_is_rejected` (strict xfail, TODO(S6-T57)).
