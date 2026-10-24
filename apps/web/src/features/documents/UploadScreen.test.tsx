// @vitest-environment jsdom
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import en from '../../../messages/en.json';
import vi_ from '../../../messages/vi.json';
import { UploadScreen } from './UploadScreen';

const push = vi.hoisted(() => vi.fn());
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }));

const PUT_URL = 'https://uploads.test/';
const PROFILE = '11111111-1111-4111-8111-111111111111';
const calls: string[] = [];
let n = 0;
const uuid = (i: number) => `00000000-0000-4000-8000-${String(i).padStart(12, '0')}`;
const out = (id: string, status: string) => ({ id, profile_id: PROFILE, status });

const server = setupServer(
  http.post('*/v1/profiles/:pid/documents', async ({ request, params }) => {
    const body = (await request.json()) as { content_type: string; size_bytes: number };
    expect(params.pid).toBe(PROFILE);
    expect(Object.keys(body).sort()).toEqual(['content_type', 'size_bytes']);
    const id = uuid(++n);
    calls.push(`create:${id.slice(-1)}`);
    return HttpResponse.json(
      { document_id: id, upload_url: `${PUT_URL}${id}`, method: 'PUT', headers: { 'Content-Type': body.content_type }, expires_in: 300 },
      { status: 201 },
    );
  }),
  http.put(`${PUT_URL}:id`, ({ params }) => {
    calls.push(`put:${String(params.id).slice(-1)}`);
    return new HttpResponse(null, { status: 200 });
  }),
  http.post('*/v1/documents/:id/complete', ({ params }) => {
    calls.push(`complete:${String(params.id).slice(-1)}`);
    return HttpResponse.json(out(String(params.id), 'uploaded'));
  }),
);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  calls.length = 0;
  push.mockClear();
  n = 0;
});
afterAll(() => server.close());

const png = (name: string, size = 1000) => new File([new Uint8Array(size)], name, { type: 'image/png' });

function setup(messages = en) {
  const user = userEvent.setup({ applyAccept: false });
  const view = render(
    <NextIntlClientProvider locale="en" messages={messages}>
      <UploadScreen profileId={PROFILE} />
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
    setup(vi_ as typeof en);
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
    await waitFor(() => expect(push).toHaveBeenCalledTimes(1));
    expect(calls).toEqual(['create:1', 'put:1', 'complete:1', 'create:2', 'put:2', 'complete:2']);
    expect(push).toHaveBeenCalledWith(`/en/documents/${uuid(1)}/progress`);
  });

  it('keeps the selection and continues after a network error', async () => {
    let fail = true;
    server.use(
      http.put(`${PUT_URL}:id`, () => {
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
    await waitFor(() => expect(calls).toContain('complete:1'));
    expect(calls.filter((c) => c.startsWith('create'))).toHaveLength(1);
  });
});
