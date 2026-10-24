import type { Page } from '@playwright/test';

// Synthetic ids/values only.
export const DOC_ID = '11111111-1111-4111-8111-111111111111';
export const PROFILE_ID = '22222222-2222-4222-8222-222222222222';
export const OTHER_USERS_DOC = '99999999-9999-4999-8999-999999999999';

// 1x1 transparent PNG.
export const PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
  'base64',
);

const json = (body: unknown, status = 200) => ({
  status,
  contentType: 'application/json',
  body: JSON.stringify(body),
});

const FIELDS = [
  { id: 'f-ok', field_path: 'patient.name', value: 'Synthetic Patient', user_value: null, confidence: 0.98, source_page: null, needs_confirmation: false, confirmed_at: null },
  { id: 'f-low', field_path: 'lab.glucose', value: '5.4', user_value: null, confidence: 0.41, source_page: null, needs_confirmation: true, confirmed_at: null },
];

/**
 * Mock the document API.
 * `statuses`: sequence GET /documents/{id} walks through (last one repeats).
 * `staleConfirm`: the first confirm after the field edit still answers 422 (server-side BR-012 guard
 * disagreeing with a stale client), proving the UI surfaces `field_ids` from the API.
 */
export async function mockApi(page: Page, opts: { statuses?: string[]; staleConfirm?: boolean } = {}) {
  const statuses = opts.statuses ?? ['uploaded', 'ocr_done', 'needs_review'];
  const calls = { puts: 0, confirm: 0 };
  let polls = 0;
  let lowConfirmed = false;
  const origin = () => new URL(page.url()).origin;

  await page.route('**/v1/profiles/*/documents', (r) =>
    r.fulfill(json({ document_id: DOC_ID, upload_url: `${origin()}/__storage/put`, method: 'PUT', headers: {}, expires_in: 300 }, 201)),
  );
  await page.route('**/__storage/put', (r) => {
    calls.puts++;
    return r.fulfill({ status: 200, body: '' });
  });
  await page.route('**/v1/documents/*/complete', (r) =>
    r.fulfill(json({ id: DOC_ID, profile_id: PROFILE_ID, status: 'uploaded' })),
  );
  await page.route(`**/v1/documents/${DOC_ID}`, (r) => {
    const status = statuses[Math.min(polls++, statuses.length - 1)]!;
    return r.fulfill(json({ id: DOC_ID, profile_id: PROFILE_ID, status }));
  });
  await page.route(`**/v1/documents/${DOC_ID}/fields`, (r) =>
    r.fulfill(json(FIELDS.map((f) => (f.id === 'f-low' && lowConfirmed ? { ...f, confirmed_at: '2026-01-01T00:00:00Z' } : f)))),
  );
  await page.route(`**/v1/documents/${DOC_ID}/fields/f-low`, (r) => {
    lowConfirmed = true;
    return r.fulfill(json({ ...FIELDS[1], user_value: r.request().postDataJSON().user_value, confirmed_at: '2026-01-01T00:00:00Z' }));
  });
  await page.route(`**/v1/documents/${DOC_ID}/confirm`, (r) => {
    calls.confirm++;
    const blocked = !lowConfirmed || (opts.staleConfirm && calls.confirm === 1);
    return blocked
      ? r.fulfill(json({ title: 'Unconfirmed fields', field_ids: ['f-low'] }, 422))
      : r.fulfill(json({ status: 'confirmed' }));
  });
  // Ownership (RLS/Cedar): another user's document looks exactly like a missing one.
  await page.route(`**/v1/documents/${OTHER_USERS_DOC}**`, (r) => r.fulfill(json({ title: 'Not found' }, 404)));
  return calls;
}
