# Compatibility matrix (NFR-17)

NFR-17: last 2 versions of Chrome, Safari, Firefox, Edge; iOS 16+, Android 10+ (plan section 16.1). Playwright projects in `tests/e2e/playwright.config.ts` approximate this with engines and device profiles. Status below comes only from the run recorded in the PR for S7-T67 (Playwright 1.55.1, bundled browsers, API mocked with `page.route`, synthetic data). Edge is covered by the Chromium engine, not run as a branded browser.

| Project | Engine / profile | TC-SMOKE-01 | TC-E2E-01 upload to confirm | TC-E2E-02 not-found | TC-E2E-03 rejected upload |
| --- | --- | --- | --- | --- | --- |
| chromium | Desktop Chrome | pass | pass | pass | pass |
| firefox | Desktop Firefox | pass | pass | pass | pass |
| webkit | Desktop Safari | not run | not run | not run | not run |
| android-pixel7 | Pixel 7 (Chromium emulation) | pass | pass | pass | pass |
| ios-iphone14 | iPhone 14 (WebKit emulation) | not run | not run | not run | not run |

"not run": the WebKit launch failed on the dev host for missing system libraries (needs `sudo npx playwright install-deps webkit`). Nothing is claimed for it.

## Flows
- TC-E2E-01: PNG upload, progress to ready, review; confirm button disabled while a low-confidence field is unchecked (BR-012); stale-client confirm returns 422 with `field_ids` and the UI lists them; confirm succeeds on retry.
- TC-E2E-02: another user's document id returns 404; review and progress show a neutral not-found/error state, no fields, no "ready" link.
- TC-E2E-03: unsupported file type and server-rejected document both show guidance and an "Upload again" path.

## How to run
```
pnpm install
npx --yes playwright install chromium firefox webkit   # browsers, once
make e2e                                               # all projects; starts the web dev server itself
pnpm --filter @medilens/web e2e --project=firefox      # one project
E2E_BASE_URL=https://staging.example pnpm --filter @medilens/web e2e   # skip own server
```
The config sets a synthetic `AUTH_SECRET` and dummy OIDC values; the session is a minted Auth.js JWT (`tests/e2e/fixtures/session.ts`). The API is fully mocked (`fixtures/api.ts`), so no backend is needed.

## Gaps
- WebKit and iPhone 14 unverified here; run on a host with the WebKit libs (CI image with `playwright install --with-deps`).
- Branded Edge and Safari, real iOS 16 / Android 10 devices, and "last 2 versions" are not covered; consider BrowserStack before beta.
- API is mocked, so contract drift is caught only by the API contract tests, not here.
- CI wiring (not done, no workflow changes in this PR): a job running `pnpm install --frozen-lockfile`, `npx playwright install --with-deps chromium firefox webkit`, `make e2e`, uploading the HTML report and traces on failure.
