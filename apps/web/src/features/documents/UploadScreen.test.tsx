// @vitest-environment jsdom
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import en from '../../../messages/en.json';
import vi from '../../../messages/vi.json';
import { UploadScreen } from './UploadScreen';

const PUT_URL = 'https://uploads.test/doc-1/';
const calls: string[] = [];
let statuses: object[] = [];

const server = setupServer(
  http.post('*/v1/profiles/:pid/documents', async ({ request }) => {
    const body = (await request.json()) as { pages: unknown[] };
    calls.push(`create:${body.pages.length}`);
    return HttpResponse.json({
      document_id: 'doc-1',
      uploads: body.pages.map((_, i) => ({ url: `${PUT_URL}${i}` })),
    });
  }),
  http.put(`${PUT_URL}:i`, ({ params }) => {
    calls.push(`put:${String(params.i)}`);
    return new HttpResponse(null, { status: 200 });
  }),
  http.post('*/v1/documents/:id/complete', () => {
    calls.push('complete');
    return new HttpResponse(null, { status: 204 });
  }),
  http.get('*/v1/documents/:id', () => HttpResponse.json(statuses.shift() ?? { status: 'queued' })),
);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  calls.length = 0;
  statuses = [];
});
afterAll(() => server.close());

const png = (name: string, size = 1000) => new File([new Uint8Array(size)], name, { type: 'image/png' });

function setup(messages = en) {
  const user = userEvent.setup({ applyAccept: false });
  const view = render(
    <NextIntlClientProvider locale="en" messages={messages}>
      <UploadScreen profileId="me" pollMs={10} />
    </NextIntlClientProvider>,
  );
  const input = view.container.querySelector<HTMLInputElement>('input[type=file]:not([capture])')!;
  return { user, input, view };
}

describe('UploadScreen', () => {
  it('has no axe violations (empty and with a selected page)', async () => {
    const { user, input, view } = setup();
    expect(await axe(view.container)).toHaveNoViolations();
    await user.upload(input, png('a.png'));
    await screen.findByText(/Page 1/);
    expect(await axe(view.container)).toHaveNoViolations();
  });

  it('shows the capture tips and the Vietnamese copy', () => {
    setup(vi as typeof en);
    expect(screen.getByText('Mẹo để ảnh rõ nét')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Chụp ảnh' })).toBeInTheDocument();
  });

  it('rejects a wrong type and an oversized file with friendly messages', async () => {
    const { user, input } = setup();
    await user.upload(input, new File(['x'], 'virus.exe', { type: 'application/x-msdownload' }));
    expect(await screen.findByText(/virus\.exe: this format isn't supported/)).toBeInTheDocument();
    await user.upload(input, png('big.png', 21 * 1024 * 1024));
    expect(await screen.findByText(/big\.png: the file is too large/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled();
  });

  it('reorders and removes pages, and uploads them in order', async () => {
    const { user, input } = setup();
    await user.upload(input, [png('a.png'), png('b.png'), png('c.png')]);
    await user.click(await screen.findByRole('button', { name: 'Move b.png up' }));
    await user.click(screen.getByRole('button', { name: 'Remove c.png' }));
    const items = screen.getAllByRole('listitem').map((li) => li.textContent);
    expect(items[0]).toContain('b.png');
    expect(items[1]).toContain('a.png');

    await user.click(screen.getByRole('button', { name: 'Upload' }));
    await screen.findByText(/Reading your record/);
    expect(calls).toEqual(['create:2', 'put:0', 'put:1', 'complete']);
    expect(screen.getByText(/You can leave this page/)).toBeInTheDocument();
  });

  it.each([
    ['blurry', /a bit blurry/],
    ['too_dark', /too dark/],
    ['not_a_document', /couldn't see a document page/],
  ])('explains the retake reason %s and lets the user retake', async (reason, text) => {
    statuses = [{ status: 'needs_retake', retake_reason: reason }];
    const { user, input, view } = setup();
    await user.upload(input, png('a.png'));
    await user.click(await screen.findByRole('button', { name: 'Upload' }));
    expect(await screen.findByText(text)).toBeInTheDocument();
    expect(await axe(view.container)).toHaveNoViolations();
    await user.click(screen.getByRole('button', { name: 'Retake' }));
    expect(screen.getByRole('button', { name: 'Take photo' })).toBeInTheDocument();
  });

  it('keeps the selection and continues after a network error', async () => {
    let fail = true;
    server.use(
      http.put(`${PUT_URL}:i`, () => {
        if (fail) return HttpResponse.error();
        return new HttpResponse(null, { status: 200 });
      }),
    );
    const { user, input } = setup();
    await user.upload(input, png('a.png'));
    await user.click(await screen.findByRole('button', { name: 'Upload' }));
    expect(await screen.findByText(/Connection lost/)).toBeInTheDocument();
    expect(screen.getByText(/a\.png/)).toBeInTheDocument();
    fail = false;
    await user.click(screen.getByRole('button', { name: 'Retry' }));
    await waitFor(() => expect(calls).toContain('complete'));
    expect(calls.filter((c) => c.startsWith('create'))).toHaveLength(1);
  });
});
