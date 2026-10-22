# E2E (Playwright)

Critical cross-app flows only (RULES C4). Synthetic data only. Strategy: `docs/qa/test-strategy.md`.

## Run
1. Start the web app: `make web-dev` (default `http://localhost:3000`), or point `E2E_BASE_URL` at staging.
2. Install a browser once (nothing is committed): `npx --yes playwright install chromium`
3. Run: `E2E_BASE_URL=http://localhost:3000 npx --yes playwright test -c tests/e2e`

`make e2e` currently calls `pnpm --filter @medilens/web e2e`, which does not exist yet. Wiring it (add `@playwright/test` to devDependencies and an `e2e` script pointing at this config) is a follow-up.

## Conventions
- Test names start with the TC id from `docs/requirements/traceability.csv`.
- Use roles and visible text, not CSS selectors. Severity is shown as a label, not colour only.
- No network beyond the app under test; no shared state between tests.
- The smoke test reads the English copy; update it if `home.disclaimer` in `apps/web/messages/en.json` changes.
- Next: fixtures for signed-in synthetic users, axe check (`@axe-core/playwright`), visual baselines per Unit.
