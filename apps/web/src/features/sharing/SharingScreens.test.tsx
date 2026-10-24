// @vitest-environment jsdom
import { QueryClientProvider } from '@tanstack/react-query';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import en from '../../../messages/en.json';
import vi_ from '../../../messages/vi.json';
import { newClient } from '../timeline/api';
import { ShareSettings, SharedView } from './SharingScreens';

vi.mock('../viewer/BodyViewer', () => ({ BodyViewer: ({ regions }: { regions: unknown[] }) => <div data-testid="viewer">{regions.length}</div> }));

const P = '11111111-1111-4111-8111-111111111111';
const G = '22222222-2222-4222-8222-222222222222';
const S = '33333333-3333-4333-8333-333333333333';
const future = new Date(Date.now() + 3 * 86_400_000).toISOString();
const mk = (id: string, over: Record<string, unknown> = {}) => ({
  id, profile_id: P, grantee_user_id: G, scope: 'findings:read', expires_at: future, revoked_at: null, ...over,
});

let shares: unknown[] = [];
let posted: unknown;
const server = setupServer(
  http.get('*/v1/profiles/:id/shares', () => HttpResponse.json(shares)),
  http.post('*/v1/profiles/:id/shares', async ({ request }) => {
    posted = await request.json();
    const s = mk(S);
    shares = [s];
    return HttpResponse.json(s, { status: 201 });
  }),
  http.delete('*/v1/shares/:id', () => {
    shares = (shares as ReturnType<typeof mk>[]).map((s) => ({ ...s, revoked_at: new Date().toISOString() }));
    return new HttpResponse(null, { status: 204 });
  }),
  http.get('*/v1/me', () => HttpResponse.json({ sub: 'abcdef12-0000-4000-8000-000000000000' })),
);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => { server.resetHandlers(); shares = []; });
afterAll(() => server.close());

const mount = (ui: React.ReactNode, messages: typeof en = en) =>
  render(
    <QueryClientProvider client={newClient()}>
      <NextIntlClientProvider locale="en" messages={messages}>{ui}</NextIntlClientProvider>
    </QueryClientProvider>,
  );

describe('ShareSettings', () => {
  it('creates, lists and revokes with confirmation', async () => {
    const { container } = mount(<ShareSettings profileId={P} />);
    expect(await screen.findByText("You haven't shared anything yet.")).toBeInTheDocument();
    expect(screen.getByText(/Access ends automatically/)).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText('Recipient user ID'), 'nope');
    await userEvent.click(screen.getByRole('button', { name: 'Create share' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/valid user ID/);

    await userEvent.clear(screen.getByLabelText('Recipient user ID'));
    await userEvent.type(screen.getByLabelText('Recipient user ID'), G);
    await userEvent.selectOptions(screen.getByLabelText('Valid for'), '24');
    await userEvent.click(screen.getByRole('button', { name: 'Create share' }));
    expect(await screen.findByText('Share created.')).toBeInTheDocument();
    expect(posted).toEqual({ grantee_user_id: G, expires_in_hours: 24 });

    const item = await screen.findByRole('listitem');
    expect(item).toHaveTextContent('Active');
    expect(item).toHaveTextContent('3 days left');
    expect(await axe(container)).toHaveNoViolations();

    await userEvent.click(within(item).getByRole('button', { name: /Revoke/ }));
    expect(screen.getByText('Revoke access for 22222222 now?')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Yes, revoke' }));
    expect(await screen.findByText(/Revoked/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Revoke/ })).not.toBeInTheDocument();
  });

  it('shows expired status and renders Vietnamese', async () => {
    shares = [mk(S, { expires_at: '2020-01-01T00:00:00Z' })];
    mount(<ShareSettings profileId={P} />, vi_ as typeof en);
    expect(await screen.findByText(/Đã hết hạn/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Tạo chia sẻ' })).toBeInTheDocument();
  });
});

describe('SharedView', () => {
  it('shows a click-through aria-hidden watermark and a banner', async () => {
    server.use(http.get('*/v1/shared/:id/findings', () => HttpResponse.json({
      findings: [{ region_code: 'heart', laterality: null, severity: 'mild', unit_code: null, is_metastasis: false, observed_at: null, label: null }],
      next_cursor: null,
    })));
    const { container } = mount(<SharedView shareId={S} expiresAt={future} />);
    const wm = await screen.findByTestId('watermark');
    expect(wm).toHaveAttribute('aria-hidden', 'true');
    expect(wm.className).toContain('pointer-events-none');
    expect(wm.textContent).toContain('abcdef12');
    expect(wm.textContent).toContain('33333333');
    expect(screen.getByRole('status')).toHaveTextContent(/View only.*abcdef12/);
    expect(screen.getByTestId('viewer')).toBeInTheDocument();
    expect(screen.getByRole('list')).toHaveTextContent('Heart');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows the access-ended page when expired or revoked', async () => {
    server.use(http.get('*/v1/shared/:id/findings', () => HttpResponse.json({ title: 'Forbidden' }, { status: 403 })));
    mount(<SharedView shareId={S} />);
    expect(await screen.findByText('Access has ended')).toBeInTheDocument();
    expect(screen.queryByTestId('watermark')).not.toBeInTheDocument();
  });
});
