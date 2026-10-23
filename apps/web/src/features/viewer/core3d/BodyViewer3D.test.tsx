// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { describe, expect, it, vi } from 'vitest';
import en from '../../../../messages/en.json';
import { BodyViewer3D } from './BodyViewer3D';

// WebGL is unavailable in jsdom; picking and camera ease are verified manually in a browser.
vi.mock('./Scene3D', () => ({ default: () => <div data-testid="scene" /> }));

const regions = [
  { region_code: 'heart', severity: 'severe' as const, label: 'Heart' },
  { region_code: 'liver', severity: 'mild' as const, label: 'Liver' },
];
const view = (onSelect?: (c: string | null) => void) =>
  render(
    <NextIntlClientProvider locale="en" messages={en}>
      <BodyViewer3D regions={regions} model="body" onSelect={onSelect} />
    </NextIntlClientProvider>,
  );

describe('BodyViewer3D list alternative', () => {
  it('selects a region from the list, shows text severity, and Escape clears', async () => {
    const onSelect = vi.fn();
    view(onSelect);
    await userEvent.click(screen.getByRole('button', { name: 'Heart: Severe' }));
    expect(screen.getByTestId('detail')).toHaveTextContent('Heart: Severe');
    expect(onSelect).toHaveBeenLastCalledWith('heart');
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByTestId('detail')).toBeNull();
    expect(onSelect).toHaveBeenLastCalledWith(null);
  });

  it('has no axe violations with a selection', async () => {
    const { container } = view();
    await userEvent.click(screen.getByRole('button', { name: 'Liver: Mild' }));
    expect(await axe(container)).toHaveNoViolations();
  });
});
