import { expect, test } from '@playwright/test';

// TC-SMOKE-01: the public home page loads and shows the disclaimer copy.
// Copy comes from apps/web/messages/en.json (home.disclaimer).
test('TC-SMOKE-01 public home shows the disclaimer', async ({ page }) => {
  const response = await page.goto('/en');
  expect(response?.ok()).toBeTruthy();
  await expect(page.getByRole('heading', { name: 'MediLens' })).toBeVisible();
  await expect(
    page.getByText("MediLens helps you understand your own medical records. Use it alongside your doctor's advice."),
  ).toBeVisible();
});
