# Security review: upload path vs SEC-AP-07 (S6-T58)

Date 2026-10-23. Reviewer: security-engineer. Base: `origin/main` @ ff2a222. Method: code and IaC read, plus two throw-away probes (PDF regex, presigned URL headers) and a PII scan of a locally generated test log. No code changed; synthetic data only.
Refs: SEC-AP-07/07a, SEC-DP-05, SEC-AP-08, SEC-AR-09, SEC-DP-06; threat model U-02/U-05/U-06/U-08/U-09/U-10; abuse cases AC-02/AC-03/AC-04/AC-07.
Severity scale: Critical/High/Medium/Low per the skill's triage (SLA 24 h / 7 d / 30 d / 90 d). Rated for the real-data target; "today" notes the current synthetic-only maturity level A.

## Verdict

**SEC-AP-07: PARTIAL, not met.** Highest open severity: **High** (F1, F4). Acceptable for synthetic data only (maturity level A). **NO-GO for real patient data** (gate G3-P) until F1, F2, F3, F4 and F6 are closed. Staging does not exist yet, so nothing here was verified against a live account; infra findings are from Terraform on main.

## Control table

| Control | Requirement | Evidence (main) | Status | Finding / follow-up |
|---|---|---|---|---|
| SEC-AP-07 magic bytes (API) | Content sniffed and equal to declared type | `apps/api/src/medilens/modules/document/application/service.py:89`; tests `test_declared_type_must_match_content`, `test_eicar_renamed_is_rejected`, `test_html_without_magic_is_rejected` | met | - |
| SEC-AP-07 magic bytes (worker) | Re-check before promote | `apps/worker/src/medilens_worker/intake/validate.py:64-68`; `test_rejections` | met | F11 (sniff table copied, drift risk) |
| SEC-AP-07 size limit | <= 20 MB (BR-010) at presign, complete, worker | `service.py:55,86`, `validate.py:56`; `test_oversize_declared_is_413`, `test_oversize_actual_is_413_and_object_removed`, `test_too_large` | met | - |
| SEC-AP-07 duplicates | Per-profile sha256, race-safe | `service.py:92-100`, unique index; `test_duplicate_sha256_per_profile`, `test_concurrent_duplicate_is_caught_by_unique_index` | met | digest is not re-checked by the worker (F6) |
| SEC-AP-07 malware scan | GuardDuty scan, no promote without clean verdict | IaC `infra/terraform/modules/storage/main.tf:262-325`; worker gate `validate.py:52-62`; `test_malware_scan_paths` | **gap** | F1: gate is off unless `WORKER_REQUIRE_MALWARE_SCAN=true`; staging env sets nothing (`infra/terraform/envs/staging/services.tf:278-283`). Fail-open default |
| SEC-AP-07 PDF active content | Reject JS/Launch/embedded | `validate.py:15,70`; `test_rejections` | **partial** | F3: evadable (confirmed, below) |
| SEC-AP-07 sandboxed parse, PDF to image | Decode only in sandbox, re-encode | none on main (`docs/qa/upload-malicious-files.md` rows 7-8: "NOT blocked yet") | **gap** | F4 |
| SEC-AP-07a promote by VersionId + checksum | No TOCTOU after scan | none: `apps/worker/src/medilens_worker/storage/s3.py:30-37` reads the latest version, no VersionId/sha check; bucket policy has no overwrite deny (`storage/main.tf:192-226`) | **gap** | F6 (already `planned`) |
| SEC-AR-09 | Parse only in sandboxed worker after scan | no sandbox; `validate.py` parses in the worker task itself | **gap** | F4 |
| SEC-DP-05 TTL | Presigned URL <= 5 min | `domain/models.py:9` (300 s); `test_presigned_url_expiry_is_at_most_five_minutes` | met | - |
| SEC-DP-05 content-type / size conditions | S3 rejects other type or size | `infra/s3_storage.py:159-169`. Probe: generated URL has `X-Amz-SignedHeaders=content-length;content-type;host`, so S3 rejects any other length/type | **partial** | Correct in practice but no test asserts it (F11). A POST policy `content-length-range` is not used; exact-length signing is equivalent |
| SEC-AP-08 pending cap | Per-user cap on in-flight uploads | `models.py:15`, `service.py:57`; `test_pending_upload_cap_is_429_per_user`, `test_old_pending_uploads_do_not_count_toward_cap` | met (cap only) | - |
| SEC-AP-08 rate / daily quota | Rate limit per user/IP/endpoint, daily quota | `rate_limit.py` `check_upload_allowed` (10 requests/min, 50 documents/day per authenticated subject, 429 + Retry-After); `tests/document/test_rate_limit.py`. WAF rate rule and k6 test still pending | **met (app layer)** | F7 fixed in app; per-process state, Redis when scaled out |
| U-08 quarantine TTL | Rejected files gone in 24 h | lifecycle `storage/main.tf:235-246`; default `quarantine_expiration_days = 7` (`storage/variables.tf:39`), dev = 7 (`envs/dev/storage.tf:12`) | **partial** | F8: 7 d vs 24 h; API deletes on reject (`service.py:113`) but worker reject and promoted originals stay until TTL; no age alarm |
| IAM: worker reads quarantine | `GetObject`, `GetObjectTagging`, KMS decrypt on quarantine; write to raw store | `envs/staging/services.tf:212-243` (`worker_task`): only SQS, `phi/extractions/*` PutObject, RDS, one KMS key. Staging does not instantiate `modules/storage` | **gap** | F2: worker cannot `head_object`/`get_object_tagging`/`get_object` (`storage/s3.py:30-37`) and has no `s3:PutObject` on `raw/*`. Fails closed (jobs retry then DLQ) |
| IAM: API signer | `PutObject` (signing identity), `GetObject`, `DeleteObject` on quarantine | `api_task` (`services.tf:179-210`): only `phi/extractions/*` GetObject | **gap** | F2: presigned PUT would 403; complete/delete would fail |
| SEC-DP-06 logs carry ids only | No PHI/URLs/payloads in logs | `apps/api/src/medilens/shared/outbox_relay.py:48` logs event type; worker `pipeline/runner.py:31-34` logs ids/step/reason; no logging in `modules/document/**` | met | F12 (note), scan below |
| U-10 job tamper | Worker re-checks the object belongs to the document | `validate.py:49-51` checks only prefix `quarantine/` and `..` | partial | F10 |

## Probes (not committed)

- `/S /J#61vaScript` (hex-escaped name): `_ACTIVE` returns no match. `/OpenAction`, `/AA`: not in the pattern. An `/ObjStm` stream hides names and `/Type /Page` objects from `_PAGE` (count 0), so the 50-page cap (`validate.py:14`) is bypassable. Confirms the known "evadable" item.
- Status BUG-14: PDF names normalised (`#xx`, whitespace), `trailing_data` and `pdf_polyglot` rejections added, image polyglots covered by re-encode tests; sandboxed parser (F4b) still open.
- Polyglots (original finding): JPEG+ZIP and `%PDF-`+HTML pass API and worker (documented, `test_content_level_payloads_pass_api_and_are_left_to_worker`). They stay valid until a sandboxed decode/re-encode exists.
- Scan-pending budget: `RetryPolicy` is 3 attempts, delays 5 s then 10 s (`pipeline/runner.py:16-22`). `ScanPending` is a plain exception, so after about 15 s the job goes to DLQ and the document to `FAILED`. A scan slower than that rejects a clean file (safe, but an availability bug). Not tested against real GuardDuty timing.

## Findings

| ID | Severity | Issue | Exploit / impact | SEC | Follow-up |
|---|---|---|---|---|---|
| F1 | High | Worker scan gate defaults off (`WORKER_REQUIRE_MALWARE_SCAN` unset) | Unscanned file promoted to `raw/` and parsed | SEC-AP-07 | S6-T58-F1 (infra: env set in staging, S6-T58-F2; app default pending) |
| F2 | Medium (today: availability) | Staging IAM and env miss quarantine access for worker and API; storage module not wired | Upload cannot work in staging; the fix must stay least-privilege (no `s3:*`, no wildcard bucket) | SEC-AP-07, SEC-DP-05 | S6-T58-F2 (infra done in PR, not applied) |
| F3 | Medium | Byte-regex PDF check evadable (hex-escaped names, object streams, missing `/OpenAction`, `/AA`, `/URI`, `/SubmitForm`, `/XFA`, `/RichMedia`); page cap bypass | Active PDF reaches OCR/rasteriser; page-count DoS | SEC-AP-07 | S6-T58-F3 |
| F4 | High (before real data; Medium today) | No sandboxed parser; polyglot JPEG+ZIP and `%PDF`+HTML accepted; no decode/re-encode, EXIF not stripped (U-11), no decompression-bomb limit (`MAX_IMAGE_PIXELS` unset in worker) | Parser exploit in the worker task that holds PHI-capable credentials | SEC-AP-07, SEC-AR-09, U-05 | S6-T58-F4 |
| F5 | Medium | Scan-pending uses the generic 3-attempt, 15 s retry | Clean files fail when GuardDuty is slower than 15 s | SEC-AP-07 | S6-T58-F5 |
| F6 | Medium | No SEC-AP-07a: no VersionId/checksum pinning, no overwrite deny; presigned URL stays valid up to 5 min after `complete` | Object replaced after API sniff/hash (worker re-sniffs magic, so impact is limited to a content swap of the same type) | SEC-AP-07a, U-06 | S6-T58-F6 (infra: versioning on, no S3 overwrite deny possible; VersionId+sha256 in app pending) |
| F7 | Medium | **Fixed (app layer, S6-F7)**: per-user rate + daily quota + SSE stream cap, `test_rate_limit.py`; WAF rule and k6 pending. Was: only a pending cap; no rate limit, daily quota or WAF rate rule evidence | Storage and scan cost abuse (AC-07) | SEC-AP-08, U-09 | S6-T58-F7 |
| F8 | Low | Quarantine TTL 7 d vs 24 h; worker reject keeps the object; no age alarm | Rejected files linger (U-08) | U-08 | S6-T58-F8 (TTL 1 d set in staging, S6-T58-F2; age alarm pending) |
| F9 | Low | Rejected document stays `uploaded-pending` (strict xfail `test_rejected_document_status_is_rejected`) | Wrong state shown; counts toward the cap for up to 10 min | SEC-AP-08 | S6-T58-F9 |
| F10 | Low | Worker trusts `storageKey` from the message (prefix check only) | Needs queue write access; defence in depth for U-10 | SEC-AZ-02 | S6-T58-F10 |
| F11 | Low | No test for signed `content-length`/`content-type`; HEIC/sniff table duplicated in API and worker | Silent regression of SEC-DP-05; drift | SEC-DP-05 | S6-T58-F11 |
| F12 | Low | Test log at DEBUG shows botocore request lines with S3 keys; prod must not run botocore at DEBUG | If `log_level=DEBUG` in prod, signed request detail is logged | SEC-DP-06 | S6-T58-F12 |

## Follow-up proposals

| ID | Owner skill | Paths | Change |
|---|---|---|---|
| S6-T58-F1 | medilens-backend-engineer | `apps/worker/src/medilens_worker/intake/validate.py`, `apps/worker/tests/intake/`, `infra/terraform/envs/staging/services.tf` | Default `require_scan` true unless `APP_ENV=local`; set env in staging |
| S6-T58-F2 | medilens-cloud-devops-engineer | `infra/terraform/envs/staging/` | Wire storage module; worker: GetObject/GetObjectTagging on `quarantine/*`, PutObject `raw/*`, KMS; API: PutObject/GetObject/DeleteObject on `quarantine/*`; set bucket env vars |
| S6-T58-F3 | medilens-ai-ml-engineer | `apps/worker/src/medilens_worker/intake/validate.py`, `apps/worker/tests/intake/` | Replace regex with a real PDF parser (resolve names, object streams); extend the name list; count pages from the parser |
| S6-T58-F4 | medilens-ai-ml-engineer + medilens-cloud-devops-engineer | `apps/worker/src/medilens_worker/ocr/`, `infra/terraform/modules/ecs-service/` | Sandboxed decode and re-encode (PDF to image, JPEG/PNG re-encode, strip EXIF, pixel cap), no credentials in the sandbox |
| S6-T58-F5 | medilens-backend-engineer | `apps/worker/src/medilens_worker/pipeline/runner.py`, `apps/worker/src/medilens_worker/jobs/registry.py` | Separate scan-pending policy: longer delays (up to about 10 min) that do not consume the failure budget |
| S6-T58-F6 | medilens-backend-engineer + medilens-cloud-devops-engineer | `apps/api/src/medilens/modules/document/`, `apps/worker/src/medilens_worker/storage/s3.py`, `infra/terraform/modules/storage/main.tf` | Carry VersionId + sha256 in the job; worker reads that version and verifies; deny overwrite after complete |
| S6-T58-F7 | medilens-backend-engineer | `apps/api/src/medilens/modules/document/`, `infra/terraform/envs/staging/services.tf`, `tests/load/` | Per-user daily upload quota and rate limit; WAF rate rule; k6 test for AC-07 |
| S6-T58-F8 | medilens-cloud-devops-engineer | `infra/terraform/envs/`, `infra/terraform/modules/storage/` | `quarantine_expiration_days = 1` in staging/prod; age alarm; worker deletes on reject |
| S6-T58-F9 | medilens-backend-engineer | `apps/api/src/medilens/modules/document/`, `apps/api/tests/document/test_malicious_uploads.py` | Add `rejected` status and clear the xfail |
| S6-T58-F10 | medilens-backend-engineer | `apps/worker/src/medilens_worker/intake/validate.py` | Require `storageKey` to end with `/<documentId>` |
| S6-T58-F11 | medilens-qa-engineer | `apps/api/tests/document/test_upload.py` | Assert SignedHeaders include content-length and content-type; test the sniff table is shared or equal |
| S6-T58-F12 | medilens-backend-engineer | `apps/api/src/medilens/core/logging.py` | Pin `botocore`/`urllib3` loggers to WARNING |

## PII scan (SEC-DP-06)

Staging does not exist, so there are no staging logs. Producible locally: `uv run pytest apps/api/tests/document apps/worker/tests -o log_cli=true -o log_cli_level=DEBUG --log-file=<file> --log-file-level=DEBUG` (110 passed, 1 skipped, 1 xfailed), 2795 log lines including 18 worker JSON events. Scanned with `.claude/skills/medilens-security-engineer/scripts/scan_log_for_pii.py`: exit 1, 4 hits, all `id_12` and all false positives: 12-digit runs inside hex SigV4 signatures and request lines from botocore DEBUG logs of the in-memory S3 fake (fake credentials, no patient data). No email, phone, name, DOB, JWT, key or clinical-term hits. Worker events carry only document ids, step names and reasons. Re-run on real staging logs once staging exists (required before G3-P).
