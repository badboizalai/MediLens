# Automation Guide

## Repository layout
```
apps/api/tests/{unit,integration,contract,authz,worker}
apps/web/src/**/*.test.tsx
apps/web/e2e/{pages,fixtures,specs}   (Playwright)
tests/perf/*.js                        (k6)
ml/eval/                               (AI golden-set harness)
```

## Playwright conventions
- Page objects per screen (UploadPage, ReviewPage, ViewerPage).
- Fixtures create a fresh synthetic user via API (`/test-support/users`, enabled only in non-prod) and clean up.
- Use `getByRole`/`getByLabel`; no CSS selectors tied to styling.
- `await expect(locator).toHaveText(...)` instead of sleeps.
- Visual: `await expect(page.getByTestId('viewer')).toHaveScreenshot('dental-36-severe.png', { maxDiffPixelRatio: 0.002 })` after `viewer:ready`.
- A11y: `const results = await new AxeBuilder({ page }).analyze(); expect(results.violations.filter(v => ['serious','critical'].includes(v.impact!))).toEqual([]);`

## Test data
Synthetic records library `testdata/records/{dental,cardiology,oncology}/*.pdf|jpg` with expected JSON; IDs D-01…, C-01…, O-01…, Q-01… (quality issues). Never real records.

## CI integration
- PR: unit, integration, contract, authz, component, E2E mocked, a11y, AI eval (path-filtered).
- main: + E2E staging smoke after deploy.
- nightly: full E2E cross-browser, visual, k6 baseline, red-team suite.
- Reports: JUnit XML + HTML artefacts; coverage to PR comment.
