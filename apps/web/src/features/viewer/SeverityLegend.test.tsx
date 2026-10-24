// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';
import { severityKeys, tokens } from '@medilens/design-system';
import { axe } from 'vitest-axe';
import { describe, expect, it } from 'vitest';
import en from '../../../messages/en.json';
import vi_ from '../../../messages/vi.json';
import { SeverityLegend } from './SeverityLegend';

const view = (locale: 'en' | 'vi') =>
  render(
    <NextIntlClientProvider locale={locale} messages={locale === 'en' ? en : vi_}>
      <SeverityLegend />
    </NextIntlClientProvider>,
  );

describe('SeverityLegend', () => {
  it.each(['en', 'vi'] as const)('lists every severity with its text label (%s)', (locale) => {
    view(locale);
    expect(screen.getAllByRole('listitem')).toHaveLength(severityKeys.length);
    for (const k of severityKeys) {
      const t = tokens.color.severity[k];
      expect(screen.getByText(locale === 'vi' ? t.labelVi : t.labelEn)).toBeInTheDocument();
    }
  });

  it('has no axe violations', async () => {
    const { container } = view('en');
    expect(await axe(container)).toHaveNoViolations();
  });
});
