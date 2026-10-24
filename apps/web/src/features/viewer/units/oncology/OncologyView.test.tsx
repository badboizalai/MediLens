// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { describe, expect, it } from 'vitest';
import en from '../../../../../messages/en.json';
import { BodyMap2D } from '../../core/BodyMap2D';
import { OncologyView } from './OncologyView';

const wrap = (ui: React.ReactNode) => render(<NextIntlClientProvider locale="en" messages={en}>{ui}</NextIntlClientProvider>);
const findings = [
  { region_code: 'heart', severity: 'moderate' as const },
  { region_code: 'liver', severity: 'reference' as const, is_metastasis: true },
];

describe('OncologyView', () => {
  it('opens in summary mode with no metastasis marker or details', () => {
    const { container } = wrap(<OncologyView findings={findings} tnm="T2N0M1" />);
    expect(container.querySelector('[data-region="heart"]')).toBeTruthy();
    expect(container.querySelector('[data-region="liver"]')).toBeNull();
    expect(container.querySelector('[data-severity="spread"]')).toBeNull();
    expect(screen.queryByText('T2N0M1')).toBeNull();
    expect(screen.getByRole('button', { name: 'Show details' })).toHaveAttribute('aria-expanded', 'false');
  });

  it('shows a labelled neutral marker, TNM verbatim and a care-team prompt after "Show details"', async () => {
    const { container } = wrap(<OncologyView findings={findings} tnm="T2N0M1" />);
    await userEvent.click(screen.getByRole('button', { name: 'Show details' }));
    const m = container.querySelector('[data-region="liver"]') as SVGElement;
    expect(m).toHaveAttribute('data-severity', 'spread');
    expect(m.getAttribute('aria-label')).toContain('stated in your record');
    expect(screen.getAllByText(/stated in your record/).length).toBeGreaterThan(0);
    expect(screen.getByText('T2N0M1')).toBeInTheDocument();
    expect(screen.getByText(/T describes tumour extent/)).toBeInTheDocument();
    expect(screen.getByText(/Ask your care team/)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('starts in summary again for a new record (state is not persisted)', async () => {
    const a = wrap(<OncologyView findings={findings} />);
    await userEvent.click(screen.getByRole('button', { name: 'Show details' }));
    a.unmount();
    wrap(<OncologyView findings={findings} />);
    expect(screen.getByRole('button', { name: 'Show details' })).toBeInTheDocument();
  });
});

describe('BodyMap2D source labels (BR-040, HZ-002)', () => {
  it('labels patient_reported items "you described" with a neutral fill', () => {
    const { container } = wrap(<BodyMap2D side="front" findings={[{ region_code: 'heart', severity: 'severe', source: 'patient_reported' }]} />);
    const el = container.querySelector('[data-region="heart"]') as SVGElement;
    expect(el.style.fill).toBe('var(--ml-color-brand-surfaceMuted)');
    expect(el).toHaveAttribute('aria-label', 'Heart: you described');
    expect(screen.getAllByText('Heart: you described').length).toBeGreaterThan(0);
  });

  it('lists unmapped findings under "Not placed on the body"', async () => {
    const { container } = wrap(<BodyMap2D side="front" findings={[{ region_code: 'nowhere', severity: 'mild', label: 'Odd spot' }]} />);
    expect(screen.getByRole('heading', { name: 'Not placed on the body' })).toBeInTheDocument();
    expect(screen.getByText('Odd spot')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
