// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import en from '../../../messages/en.json';
import vi from '../../../messages/vi.json';
import { ProgressScreen } from './ProgressScreen';

const ID = '00000000-0000-4000-8000-000000000001';
const PROFILE = '11111111-1111-4111-8111-111111111111';
let queue: object[] = [];
const server = setupServer(
  http.get('*/v1/documents/:id', () => HttpResponse.json((queue.length > 1 ? queue.shift() : queue[0])!)),
);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  queue = [];
});
afterAll(() => server.close());

const doc = (status: string, extra = {}) => ({ id: ID, profile_id: PROFILE, status, ...extra });
function setup(messages = en, locale = 'en') {
  return render(
    <NextIntlClientProvider locale={locale} messages={messages}>
      <ProgressScreen documentId={ID} pollMs={10} />
    </NextIntlClientProvider>,
  );
}

describe('ProgressScreen', () => {
  it('announces stage changes in a live region, then offers the review', async () => {
    queue = [doc('uploaded'), doc('ocr_done'), doc('needs_review')];
    const view = setup();
    expect(await screen.findByText('Waiting to start', { selector: '[role=status]' })).toBeInTheDocument();
    expect(await axe(view.container)).toHaveNoViolations();
    expect(await screen.findByText('Finding the details', { selector: '[role=status]' })).toBeInTheDocument();
    const link = await screen.findByRole('link', { name: 'Check your record' });
    expect(link).toHaveAttribute('href', `/en/documents/${ID}/review`);
    expect(await axe(view.container)).toHaveNoViolations();
  });

  it.each([
    ['blurry', /a bit blurry/],
    ['not_a_document', /couldn't see a document page/],
  ])('retake (%s) gives guidance, a new-photo action and the capture guide', async (reason, text) => {
    queue = [doc('needs_retake', { retake_reason: reason })];
    const view = setup();
    expect(await screen.findByText(text)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Take a new photo' })).toHaveAttribute('href', '/en/upload');
    expect(screen.getByRole('link', { name: 'See how to take a clear photo' })).toHaveAttribute(
      'href',
      '/en/upload#capture-tips',
    );
    expect(await axe(view.container)).toHaveNoViolations();
  });

  it('rejected upload explains why and offers to upload again', async () => {
    queue = [doc('rejected')];
    const view = setup();
    expect(await screen.findByText(/not a supported type/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Upload again' })).toHaveAttribute('href', '/en/upload');
    expect(await axe(view.container)).toHaveNoViolations();
  });

  it('failed offers upload again, in Vietnamese too', async () => {
    queue = [doc('failed')];
    setup(vi as typeof en, 'vi');
    expect(await screen.findByRole('link', { name: 'Tải lên lại' })).toHaveAttribute('href', '/vi/upload');
  });

  it('an unknown status keeps waiting instead of showing an error', async () => {
    queue = [doc('brand_new_status')];
    setup();
    expect(await screen.findByText('Waiting to start', { selector: '[role=status]' })).toBeInTheDocument();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });
});
