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
import { newClient } from './api';
import { ProfileBodyScreen, TimelineScreen } from './TimelineScreen';

vi.mock('../viewer/BodyViewer', () => ({ BodyViewer: ({ regions }: { regions: unknown[] }) => <div data-testid="viewer">{regions.length}</div> }));

const P = '11111111-1111-4111-8111-111111111111';
const f = (region_code: string, doc: string, at: string) => ({
  region_code, laterality: null, severity: 'mild', unit_code: null, is_metastasis: false, observed_at: at, document_id: doc, label: null,
});
const obs = (name: string, value: string, doc: string) => ({
  name, value, unit: 'mg/dL', loinc_code: null, ref_low: null, ref_high: null, observed_at: null, document_id: doc,
});

let body = { findings: [] as unknown[], observations: [] as unknown[], next_cursor: null as string | null };
const server = setupServer(http.get('*/v1/profiles/:id/findings', () => HttpResponse.json(body)));
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const mount = (ui: React.ReactNode, messages: typeof en = en) =>
  render(
    <QueryClientProvider client={newClient()}>
      <NextIntlClientProvider locale="en" messages={messages}>{ui}</NextIntlClientProvider>
    </QueryClientProvider>,
  );

describe('TimelineScreen', () => {
  it('compares the two latest visits with a neutral text diff and a measurements table', async () => {
    body = {
      findings: [f('liver', 'd1', '2026-01-02T00:00:00Z'), f('heart', 'd1', '2026-01-02T00:00:00Z'), f('heart', 'd2', '2026-03-01T00:00:00Z'), f('brain', 'd2', '2026-03-01T00:00:00Z')],
      observations: [obs('Hb', '12', 'd1'), obs('Hb', '13', 'd2')],
      next_cursor: null,
    };
    const { container } = mount(<TimelineScreen profileId={P} />);
    expect(await screen.findByText('Differences between the two visits')).toBeInTheDocument();
    const lists = screen.getAllByRole('list');
    const text = lists.map((l) => within(l).queryAllByRole('listitem').map((i) => i.textContent));
    expect(text).toContainEqual(['Brain']); // second visit only
    expect(text).toContainEqual(['Liver']); // first visit only
    expect(text).toContainEqual(['Heart']);
    const row = screen.getByRole('row', { name: /Hb/ });
    expect(row).toHaveTextContent('12');
    expect(row).toHaveTextContent('13');
    expect(row).toHaveTextContent('mg/dL');
    expect(document.body.textContent).not.toMatch(/improved|worsened|better than|worse than/i);
    expect(await axe(container)).toHaveNoViolations();
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'First visit' }), 'd2');
    expect(screen.getAllByText('Heart').length).toBeGreaterThan(0);
  });

  it('shows empty, one-visit and error states', async () => {
    body = { findings: [], observations: [], next_cursor: null };
    const a = mount(<TimelineScreen profileId={P} />);
    expect(await screen.findByText(/No confirmed findings yet/)).toBeInTheDocument();
    a.unmount();

    body = { findings: [f('liver', 'd1', '2026-01-02T00:00:00Z')], observations: [], next_cursor: null };
    const b = mount(<TimelineScreen profileId={P} />);
    expect(await screen.findByText(/Only one visit is available/)).toBeInTheDocument();
    expect(await screen.findByTestId('viewer')).toBeInTheDocument();
    b.unmount();

    server.use(http.get('*/v1/profiles/:id/findings', () => new HttpResponse(null, { status: 500 })));
    mount(<TimelineScreen profileId={P} />);
    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load/);
  });

  it('follows the cursor and renders in Vietnamese', async () => {
    const seen: (string | null)[] = [];
    server.use(
      http.get('*/v1/profiles/:id/findings', ({ request }) => {
        const c = new URL(request.url).searchParams.get('cursor');
        seen.push(c);
        return HttpResponse.json(c
          ? { findings: [f('heart', 'd2', '2026-03-01T00:00:00Z')], observations: [], next_cursor: null }
          : { findings: [f('liver', 'd1', '2026-01-02T00:00:00Z')], observations: [], next_cursor: 'c2' });
      }),
    );
    mount(<TimelineScreen profileId={P} />, vi_ as typeof en);
    expect(await screen.findByText('Khác biệt giữa hai lần khám')).toBeInTheDocument();
    expect(seen).toEqual([null, 'c2']);
  });
});

describe('ProfileBodyScreen', () => {
  it('mounts the viewer with the latest visit only', async () => {
    body = { findings: [f('liver', 'd1', '2026-01-02T00:00:00Z'), f('heart', 'd2', '2026-03-01T00:00:00Z')], observations: [], next_cursor: null };
    mount(<ProfileBodyScreen profileId={P} />);
    expect((await screen.findByTestId('viewer')).textContent).toBe('1');
  });
});
