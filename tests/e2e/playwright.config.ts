import { defineConfig, devices } from '@playwright/test';

// Base URL of a running web app (make web-dev, or a staging URL).
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';
// Auth.js secret shared by the dev server and the test session cookie (fixtures/session.ts). Synthetic.
const AUTH_SECRET = process.env.AUTH_SECRET ?? 'e2e-only-synthetic-secret-not-for-real-use';

// NFR-17 matrix: Chrome/Firefox/Safari engines + a modern Android and iOS profile.
// Select with --project (e.g. `--project=chromium`); docs/qa/compat-matrix.md records what actually ran.
export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: { baseURL, trace: 'retain-on-failure' },
  // Start our own server unless a URL was given; the API is mocked per test.
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'pnpm --filter @medilens/web dev',
        url: 'http://localhost:3000/en',
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
        // Dummy OIDC values: Auth.js asserts a provider config; the e2e session is a minted JWT (no IdP call).
        env: {
          AUTH_SECRET,
          NEXT_PUBLIC_API_BASE_URL: '',
          AUTH_OIDC_ISSUER: 'http://127.0.0.1:9/e2e',
          AUTH_OIDC_CLIENT_ID: 'e2e',
          AUTH_OIDC_CLIENT_SECRET: 'e2e',
        },
      },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'android-pixel7', use: { ...devices['Pixel 7'] } },
    { name: 'ios-iphone14', use: { ...devices['iPhone 14'] } },
  ],
});
