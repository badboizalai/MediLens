// @vitest-environment jsdom
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import en from '../../../messages/en.json';
import vi from '../../../messages/vi.json';
import { ReviewScreen } from './ReviewScreen';

const DOC = '22222222-2222-4222-8222-222222222222';
const LOW = '33333333-3333-4333-8333-333333333333';
const OK = '44444444-4444-4444-8444-444444444444';
const row = (id: string, path: string, low: boolean, extra = {}) => ({
  id, field_path: path, value: 'raw', user_value: null, confidence: low ? 0.4 : 0.95,
  source_page: 1, source_box: null, needs_confirmation: low, confirmed_at: null, ...extra,
});

let fields: ReturnType<typeof row>[] = [];
let confirmStatus = 204;
const patches: unknown[] = [];

const server = setupServer(
  http.get('*/v1/documents/:id/fields', () => HttpResponse.json(fields)),
  http.patch('*/v1/documents/:id/fields/:fid', async ({ request, params }) => {
    const body = (await request.json()) as { user_value: string };
    patches.push(body);
    const f = fields.find((x) => x.id === params.fid)!;
    return HttpResponse.json({ ...f, user_value: body.user_value, confirmed_at: '2026-01-01T00:00:00Z' });
  }),
  http.post('*/v1/documents/:id/confirm', () =>
    confirmStatus === 409
      ? HttpResponse.json({ title: 'Unconfirmed fields remain', detail: `Confirm these low-confidence fields first: ${LOW}` }, { status: 409 })
      : new HttpResponse(null, { status: 204 }),
  ),
);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  patches.length = 0;
  confirmStatus = 204;
});
afterAll(() => server.close());

function setup(messages = en) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const view = render(
    <QueryClientProvider client={client}>
      <NextIntlClientProvider locale="en" messages={messages}>
        <ReviewScreen documentId={DOC} />
      </NextIntlClientProvider>
    </QueryClientProvider>,
  );
  return { user: userEvent.setup(), view };
}

const confirmBtn = () => screen.getByRole('button', { name: /Confirm document|Xác nhận hồ sơ/ });

describe('ReviewScreen', () => {
  it('flags low-confidence rows with text and disables confirm until they are confirmed', async () => {
    fields = [row(OK, 'finding.text', false), row(LOW, 'finding.location', true)];
    const { user, view } = setup();
    expect(await screen.findByText(/Needs check\./)).toBeInTheDocument();
    expect(screen.getAllByText(/Needs check\./)).toHaveLength(1);
    expect(screen.getByText('1 item left to check')).toBeInTheDocument();
    expect(confirmBtn()).toBeDisabled();
    expect(await axe(view.container)).toHaveNoViolations();

    // keyboard: tab to the input of the low row, confirm as-is with Enter
    await user.click(screen.getByLabelText('finding.location'));
    await user.keyboard('{Enter}');
    await waitFor(() => expect(confirmBtn()).toBeEnabled());
    expect(patches).toEqual([{ user_value: 'raw' }]);
    expect(screen.queryByText(/Needs check\./)).not.toBeInTheDocument();
  });

  it('submits an edit via PATCH and validates length', async () => {
    fields = [row(OK, 'finding.text', false)];
    const { user } = setup();
    const input = await screen.findByLabelText('finding.text');
    await user.clear(input);
    await user.click(screen.getByRole('button', { name: 'Save change' }));
    expect(await screen.findByText('Please enter a value.')).toBeInTheDocument();
    expect(patches).toEqual([]);

    await user.type(input, 'new text');
    await user.click(screen.getByRole('button', { name: 'Save change' }));
    await waitFor(() => expect(patches).toEqual([{ user_value: 'new text' }]));
    expect(await screen.findByText(/You edited/)).toBeInTheDocument();
  });

  it('lists the server ids on a 409', async () => {
    // all rows look confirmed locally, but the server disagrees
    fields = [row(LOW, 'finding.location', true, { confirmed_at: '2026-01-01T00:00:00Z' })];
    confirmStatus = 409;
    const { user } = setup();
    await screen.findByLabelText('finding.location');
    await user.click(confirmBtn());
    expect(await screen.findByText('These items still need your check:')).toBeInTheDocument();
    expect(screen.getAllByText('finding.location').length).toBeGreaterThan(1);
  });

  it('confirms the document and shows the Vietnamese copy', async () => {
    fields = [row(OK, 'finding.text', false)];
    const { user } = setup(vi as typeof en);
    await screen.findByLabelText('finding.text');
    expect(screen.getByText('Do AI trích xuất — vui lòng kiểm tra lại.')).toBeInTheDocument();
    await user.click(confirmBtn());
    expect(await screen.findByText('Đã xác nhận.')).toBeInTheDocument();
  });
});
