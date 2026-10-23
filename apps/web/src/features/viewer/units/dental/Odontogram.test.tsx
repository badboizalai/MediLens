// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { afterEach, describe, expect, it, vi } from 'vitest';
import en from '../../../../../messages/en.json';
import vi_ from '../../../../../messages/vi.json';
import { Odontogram, type OdontogramProps } from './Odontogram';

const view = (props: OdontogramProps, locale: 'en' | 'vi' = 'en') =>
  render(
    <NextIntlClientProvider locale={locale} messages={locale === 'en' ? en : vi_}>
      <Odontogram {...props} />
    </NextIntlClientProvider>,
  );

afterEach(() => vi.restoreAllMocks());

describe('Odontogram', () => {
  it('applies tooth and surface states via data attributes', () => {
    const { container } = view({ teeth: [{ fdi: '16', state: 'caries', surfaces: ['O', 'M'] }, { fdi: '36', state: 'missing' }] });
    expect(container.querySelector('#tooth_16')).toHaveAttribute('data-state', 'caries');
    expect(container.querySelector('#tooth_16__O')).toHaveAttribute('data-state', 'caries');
    expect(container.querySelector('#tooth_16__M')).toHaveAttribute('data-state', 'caries');
    expect(container.querySelector('#tooth_16__B')).not.toHaveAttribute('data-state');
    // no surfaces given: whole tooth
    expect(container.querySelector('#tooth_36__L')).toHaveAttribute('data-state', 'missing');
  });

  it('maps incisal to occlusal and palatal to lingual', () => {
    const { container } = view({ teeth: [{ fdi: '11', state: 'filled', surfaces: ['I', 'P'] }] });
    expect(container.querySelector('#tooth_11__O')).toHaveAttribute('data-state', 'filled');
    expect(container.querySelector('#tooth_11__L')).toHaveAttribute('data-state', 'filled');
    expect(container.querySelector('#tooth_11__B')).not.toHaveAttribute('data-state');
  });

  it('ignores unknown FDI with a dev warning and no throw', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { container } = view({ teeth: [{ fdi: '99', state: 'caries' }] });
    expect(container.querySelector('[data-state]')).toBeNull();
    expect(warn).toHaveBeenCalled();
    expect(screen.getByText(en.dental.empty)).toBeInTheDocument();
  });

  it('lists tooth number and state in text, in VI too', () => {
    view({ teeth: [{ fdi: '46', state: 'implant' }] }, 'vi');
    expect(screen.getByRole('listitem')).toHaveTextContent('Răng 46: Cấy ghép implant');
  });

  it('selects with Enter and Space and shows details', async () => {
    const user = userEvent.setup();
    const { container } = view({ teeth: [{ fdi: '24', state: 'caries', surfaces: ['D'] }, { fdi: '25', state: 'filled' }] });
    const t24 = container.querySelector('#tooth_24') as SVGElement;
    expect(container.querySelector('#tooth_26')).not.toHaveAttribute('tabindex');
    await user.tab();
    expect(t24).toHaveFocus();
    await user.keyboard('{Enter}');
    expect(screen.getByRole('status')).toHaveTextContent('Tooth 24: Caries noted, surfaces distal');
    expect(t24).toHaveAttribute('aria-pressed', 'true');
    await user.tab();
    await user.keyboard(' ');
    expect(screen.getByRole('status')).toHaveTextContent('Tooth 25: Filled');
    expect(t24).toHaveAttribute('aria-pressed', 'false');
  });

  it('has no axe violations', async () => {
    const { container } = view({ teeth: [{ fdi: '16', state: 'caries', surfaces: ['O'] }, { fdi: '21', state: 'implant' }] });
    expect(await axe(container)).toHaveNoViolations();
  });
});
