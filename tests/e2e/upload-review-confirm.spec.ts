import { expect, test } from '@playwright/test';
import { DOC_ID, mockApi, OTHER_USERS_DOC, PNG } from './fixtures/api';
import { signInAs } from './fixtures/session';

// Copy comes from apps/web/messages/en.json (upload, progress, review).
test.beforeEach(async ({ context, baseURL }) => {
  await signInAs(context, baseURL!);
});

test('TC-E2E-01 upload -> progress -> review -> confirm (blocked by low-confidence field, then OK)', async ({ page }) => {
  const calls = await mockApi(page, { staleConfirm: true });

  await page.goto('/en/upload');
  await page.locator('input[type=file]:not([capture])').setInputFiles({ name: 'record.png', mimeType: 'image/png', buffer: PNG });
  await expect(page.getByText('Page 1 · record.png')).toBeVisible();
  await page.getByRole('button', { name: 'Upload', exact: true }).click();
  await expect(page.getByText('Your draft is ready. Please check each field.')).toBeVisible({ timeout: 20_000 });
  expect(calls.puts).toBe(1);

  await page.goto(`/en/documents/${DOC_ID}/progress`);
  await page.getByRole('link', { name: 'Check your record' }).click();
  await expect(page).toHaveURL(new RegExp(`/documents/${DOC_ID}/review`));

  // BR-012: low-confidence field blocks confirm in the UI, with a text (not colour-only) marker.
  const confirm = page.getByRole('button', { name: 'Confirm document' });
  await expect(page.getByText('1 item left to check')).toBeVisible();
  await expect(page.getByText('Needs check.')).toBeVisible();
  await expect(confirm).toBeDisabled();

  await page.getByRole('button', { name: 'Confirm this value' }).click();
  await expect(page.getByText('All items checked')).toBeVisible();
  await expect(confirm).toBeEnabled();

  // Server still refuses once (stale client): 422 field_ids are listed by field name.
  await confirm.click();
  await expect(page.getByText('These items still need your check:')).toBeVisible();
  await expect(page.getByRole('listitem').filter({ hasText: /^lab\.glucose$/ })).toBeVisible();

  await confirm.click();
  await expect(page.getByText('Confirmed.', { exact: true })).toBeVisible();
  expect(calls.confirm).toBe(2);
});

test("TC-E2E-02 another user's document shows the not-found state and no data", async ({ page }) => {
  await mockApi(page);
  await page.goto(`/en/documents/${OTHER_USERS_DOC}/review`);
  await expect(page.getByText("We couldn't load the fields. Please try again.")).toBeVisible();
  await expect(page.getByText('Confirm document')).toHaveCount(0);
  await expect(page.getByText('patient.name')).toHaveCount(0);

  await page.goto(`/en/documents/${OTHER_USERS_DOC}/progress`);
  // Not-found must not be shown as "ready" or leak a status; the screen stays in its neutral state.
  await expect(page.getByRole('link', { name: 'Check your record' })).toHaveCount(0);
});

test('TC-E2E-03 rejected upload gives guidance (client type check and server rejection)', async ({ page }) => {
  await mockApi(page, { statuses: ['rejected'] });

  await page.goto('/en/upload');
  await page.locator('input[type=file]:not([capture])').setInputFiles({ name: 'notes.txt', mimeType: 'text/plain', buffer: Buffer.from('x') });
  await expect(page.getByText("notes.txt: this format isn't supported. Please use JPG, PNG, HEIC or PDF.")).toBeVisible();
  await expect(page.getByText('Tips for a clear photo')).toBeVisible();

  await page.goto(`/en/documents/${DOC_ID}/progress`);
  await expect(page.getByText("We couldn't accept this file")).toBeVisible();
  await expect(page.getByRole('link', { name: 'Upload again' })).toBeVisible();
});
