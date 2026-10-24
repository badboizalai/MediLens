# Regression run S11 (D107)

Run on 2026-10-24 on a dev host (WSL2, Python 3.10.22, Docker available) from branch `test/S11-T107-regression-authz` = `origin/main` @ 606f744 (after #141) plus this PR's tests. Synthetic data only. Everything below is a real result of the command shown; nothing is inferred.

## Suites

| Suite | Command | Result |
| --- | --- | --- |
| API | `cd apps/api && uv run pytest` | 221 passed (before the rebase onto #141; includes the new `tests/authz`, 3 tests) |
| Authz matrix | `cd apps/api && uv run pytest tests/authz` | 3 passed (23 routes x 6 actors + 5 public routes + classification guard) |
| Worker | `cd apps/worker && uv run pytest` | 240 passed, 8 skipped (cv2/OpenCV not installed on this host: `test_preprocess_cv.py`, 7 in `test_validate.py`) |
| ai-gateway | `cd apps/ai-gateway && uv run pytest` | 76 passed |
| phi-service | `cd apps/phi-service && uv run pytest` | 16 passed |
| Root (apps + tests + ml testpaths) | `uv run pytest` | 670 passed, 8 skipped (same cv2 skips) |
| Python lint | `uv run ruff check . && uv run ruff format --check .` | clean (686 files) |
| Architecture | `cd apps/api && uv run lint-imports` | 12 contracts kept, 0 broken |
| Governance | `make governance` | PASS (BLOCK=0 REVIEW=0; licence-register WARNs LIC-012/013 "unclear, ask Regulatory" are existing human items) |
| Web lint | `pnpm lint` | no ESLint warnings or errors |
| Web typecheck | `pnpm --filter @medilens/web typecheck` | clean |
| Web unit | `pnpm test` | 25 files, 108 tests passed |
| Web build | `pnpm --filter @medilens/web build` | built |
| E2E chromium | `pnpm --filter @medilens/web e2e --project=chromium` | **4 failed, environment**: the bundled Chromium cannot start here (exit 127, `ldd` reports `libnspr4`, `libnss3`, `libnssutil3`, `libsmime3`, `libasound` missing; needs `sudo npx playwright install-deps chromium`). Not a product result. The last recorded green run is `docs/qa/compat-matrix.md` (S7-T67): chromium, firefox, android-pixel7 pass. |

The root `uv run pytest` needs the repo's `--import-mode=importlib` (already in `addopts`); overriding `addopts` breaks collection because several apps have a `test_health.py`.

## Authorisation matrix (D107)

`apps/api/tests/authz/test_route_matrix.py` runs the real `create_app()` against Testcontainers Postgres (migrations, RLS as `app_rw`) with six actors. Result and table: `docs/qa/authz-matrix.md`.

- Every route in `app.openapi()` plus the top-level docs routes must appear in `PUBLIC` (with a reason) or `ROUTES` (with an access class). A new unclassified route, or a stale entry, fails `test_every_route_is_classified`.
- Anonymous gets 401 Problem Details on every non-public route; the five public routes (health, ready, openapi, docs) answer without a token.
- The other user, the share grantee, the admin and the admin with a break-glass grant get 404 on every owner-scoped route (no existence leak); non-admins get 403 on admin routes; only the admin with an open grant reads `/v1/admin/break-glass/{id}/documents`; only the grantee reads `/v1/shared/*` (the owner gets 404 there).
- 0 failures, no authorisation gap found by this run.
- Limits: "allow" means any status except 401/403/404/5xx, so it proves the actor is let in, not that the business result is right (module tests cover that). Expired and revoked shares, grant expiry, replayed service tokens and IDOR audit rows stay in the module suites (sharing, admin, ai-gateway, phi-service).

## Open bugs and follow-ups

Source: "Follow-ups from reviews" in `docs/operations/autopilot-state.md` (last updated at run 4) cross-checked against merged PR titles in `git log`. Severity uses the QA skill definition (S1 data exposure or crash of the main flow ... S4 cosmetic). Severities are the QA proposal; the owner confirms. No new bugs are invented here and nothing is marked fixed that the log does not show.

| Item | Source PR | Severity | State |
| --- | --- | --- | --- |
| PDF active-content regex is evadable; polyglot JPEG+ZIP and `%PDF`+HTML pass API and worker validation (sandboxed decode/re-encode not done) | #67, #69 | S2 | Open |
| Staging cannot run the pipeline end to end: relay has no runtime (ECS task), worker needs quarantine `GetObject`/`GetObjectTagging` and pages bucket, DLQ alarm actions unwired | #68, #70 | S2 | Open (deploy gap; Terraform apply is a human action) |
| Sandboxed PDF rasterisation and HEIC re-encode (F4b rest; the 50 MP pre-decode cap is done in #89) | #79 | S3 | Open |
| Result store `latest()` uses LastModified, should use a time-ordered run id | #82 | S3 | Open |
| Region SVG laterality review by the clinical informaticist; `svg_id` missing from the region tree | #66 | S3 | Open |
| Gateway: unbounded `_docs` usage map; real Bedrock adapter must report `confidence`/`schema_valid`; review logging of redacted prompts | S7-T65 | S3 | Open (the Bedrock item is future work) |
| Worker and API base images not pinned by digest; no CI build or Trivy for the worker image | S6-T58-F4b | S3 | Open |
| `PAGE_TYPE_UNIT` has no cardiology page type; dental `abbrev` not wired into the normaliser | S8 | S3 | Open (S7-T62 added the normaliser; wiring not re-checked) |
| Web STAGE map lacks `rejected` | #75 | S3 | Unverified: TC-E2E-03 (rejected upload guidance) passed in S7-T67, but the e2e did not run here |
| Shared ownership/audit port in `medilens.shared` (document and extraction query `identity.*`/`audit.*` directly) | #72 | S4 | Open (accepted precedent) |
| D55 OCR baseline and an independent template set before the classifier score is used as G2 evidence | S6-T54c | S4 | Open (evidence gap, not a defect) |

Closed by merged PRs (per `git log` titles; covered by the green suites above, not re-tested one by one): F7 rate limit/quota (#131), SSE status stream (#102), page image + bbox (#122), runner terminal guard (#92), confirm 422 with `field_ids` (#88), worker SSE-KMS (#87), 50 MP pixel cap (#89), region mapping wired (#98), extraction ingest definer (#106), BUG-09, BUG-10 (RT-001..005, RT-007), BUG-11, BUG-12, BUG-13.

Human gates, not bugs: CSO review of `draft-pending-CSO` hazard rows and dental wording (G2-CS), G0/G0-R, G1-D (LIC-002), consent-form lines 6/27 claims lint, `apps/web/.env.example`.

## Acceptance

- S1 open: 0.
- S2 open: 2 (upload polyglot hardening; staging deploy gaps). The acceptance "0 open S1/S2" is **not met**; both need an owner decision or a human action and are not fixed by this PR.
- Gaps in this run: chromium e2e not executed (host libraries), 8 worker tests skipped (no OpenCV), WebKit/iOS projects never run (`compat-matrix.md`).
