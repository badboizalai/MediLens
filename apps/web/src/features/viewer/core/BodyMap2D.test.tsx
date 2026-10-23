// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { describe, expect, it, vi } from 'vitest';
import en from '../../../../messages/en.json';
import vi_ from '../../../../messages/vi.json';
import { BodyMap2D, type BodyMap2DProps } from './BodyMap2D';

const view = (props: BodyMap2DProps, locale: 'en' | 'vi' = 'en') =>
  render(
    <NextIntlClientProvider locale={locale} messages={locale === 'en' ? en : vi_}>
      <BodyMap2D {...props} />
    </NextIntlClientProvider>,
  );

describe('BodyMap2D', () => {
  it('fills a region with its severity token and names it accessibly', () => {
    const { container } = view({ side: 'front', findings: [{ region_code: 'heart', severity: 'severe' }] });
    const el = container.querySelector('[data-region="heart"]') as SVGElement;
    expect(el.style.fill).toBe('var(--ml-color-severity-severe)');
    expect(el).toHaveAttribute('aria-label', 'Heart: Severe');
  });

  it('keeps the highest severity when a region has several findings', () => {
    const { container } = view({
      side: 'front',
      findings: [{ region_code: 'heart', severity: 'mild' }, { region_code: 'heart', severity: 'spread' }],
    });
    expect(container.querySelector('[data-region="heart"]')).toHaveAttribute('data-severity', 'spread');
  });

  it('ignores unknown codes without crashing and reports them', () => {
    const onUnknown = vi.fn();
    const { container } = view({ side: 'front', findings: [{ region_code: 'nope', severity: 'mild' }], onUnknownRegion: onUnknown });
    expect(container.querySelector('[data-region]')).toBeNull();
    expect(screen.getByText(en.viewer.empty)).toBeInTheDocument();
    expect(onUnknown).toHaveBeenCalledWith(['nope']);
  });

  it('shows the tooltip on keyboard focus and hides it on blur', async () => {
    const user = userEvent.setup();
    view({ side: 'front', findings: [{ region_code: 'heart', severity: 'moderate' }] });
    await user.tab();
    expect(screen.getByRole('tooltip')).toHaveTextContent('Heart: Moderate');
    await user.tab();
    expect(screen.queryByRole('tooltip')).toBeNull();
  });

  it('lists every region with its severity as text, in Vietnamese too', () => {
    view({ side: 'front', findings: [{ region_code: 'liver', severity: 'mild' }, { region_code: 'heart', severity: 'spread' }] }, 'vi');
    const items = screen.getAllByRole('listitem').map((li) => li.textContent);
    expect(items).toEqual(['Gan: Nhẹ', 'Tim: Di căn / lan rộng']);
  });

  it('has no axe violations', async () => {
    const { container } = view({ side: 'front', findings: [{ region_code: 'heart', severity: 'severe' }, { region_code: 'liver', severity: 'reference' }] });
    expect(await axe(container)).toHaveNoViolations();
  });
});
