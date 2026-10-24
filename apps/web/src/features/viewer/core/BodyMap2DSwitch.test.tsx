// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { describe, expect, it } from 'vitest';
import en from '../../../../messages/en.json';
import vi_ from '../../../../messages/vi.json';
import { BodyMap2DSwitch } from './BodyMap2DSwitch';

const view = (locale: 'en' | 'vi' = 'en') =>
  render(
    <NextIntlClientProvider locale={locale} messages={locale === 'en' ? en : vi_}>
      <BodyMap2DSwitch findings={[{ region_code: 'heart', severity: 'severe' }]} />
    </NextIntlClientProvider>,
  );

describe('BodyMap2DSwitch', () => {
  it('toggles the side and keeps the findings list', async () => {
    const { container } = view();
    const front = screen.getByRole('button', { name: 'Front' });
    const back = screen.getByRole('button', { name: 'Back' });
    expect(front).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('group', { name: en.viewer.front })).toBeInTheDocument();
    await userEvent.click(back);
    expect(back).toHaveAttribute('aria-pressed', 'true');
    expect(front).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByRole('group', { name: en.viewer.back })).toBeInTheDocument();
    expect(screen.getByText('Heart: Severe')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('is reachable by keyboard and translated', async () => {
    view('vi');
    await userEvent.tab();
    await userEvent.tab();
    expect(screen.getByRole('button', { name: 'Mặt sau' })).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    expect(screen.getByRole('button', { name: 'Mặt sau' })).toHaveAttribute('aria-pressed', 'true');
  });
});
