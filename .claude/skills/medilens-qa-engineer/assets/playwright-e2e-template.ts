// e2e/specs/dental-upload.spec.ts
import { test, expect } from '../fixtures';          // fixtures provide `user` (fresh synthetic account) and page objects
import AxeBuilder from '@axe-core/playwright';

test.describe('Dental record: upload → review → viewer', () => {
  test('TC-101 shows tooth 36 caries after confirmation (BR-012, BR-013, BR-020)', async ({ page, user, uploadPage, reviewPage, viewerPage }) => {
    await user.signInWithConsent(page);

    await uploadPage.open();
    await uploadPage.upload('testdata/records/dental/D-01.jpg');
    await expect(uploadPage.status).toHaveText(/Đã đọc xong|Ready for review/, { timeout: 120_000 });

    await reviewPage.openLatest();
    await expect(reviewPage.lowConfidenceFields).toHaveCount(1);
    await expect(reviewPage.confirmButton).toBeDisabled();
    await reviewPage.acceptField('teeth[0].fdi');
    await reviewPage.confirmButton.click();

    await viewerPage.open('dental');
    await viewerPage.waitReady();
    const tooth = viewerPage.findingItem('36');
    await expect(tooth).toContainText(/Sâu răng|Caries/);
    await expect(tooth.getByTestId('severity-label')).toBeVisible();     // label, not colour only

    await expect(page.getByTestId('viewer')).toHaveScreenshot('dental-D01.png', { maxDiffPixelRatio: 0.002 });

    const a11y = await new AxeBuilder({ page }).analyze();
    expect(a11y.violations.filter(v => v.impact === 'serious' || v.impact === 'critical')).toEqual([]);
  });

  test('TC-102 stranger cannot open another user\'s review (SEC-AZ-02)', async ({ page, user, otherUserDocumentId }) => {
    await user.signInWithConsent(page);
    const resp = await page.goto(`/vi/app/documents/${otherUserDocumentId}/review`);
    expect(resp?.status()).toBe(404);
  });
});
