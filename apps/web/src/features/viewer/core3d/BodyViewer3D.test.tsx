// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import en from '../../../../messages/en.json';
import { BodyViewer3D } from './BodyViewer3D';

// WebGL is unavailable in jsdom; picking and camera ease are verified manually in a browser.
const cam = { rotate: vi.fn(), zoom: vi.fn(), reset: vi.fn() };
vi.mock('./Scene3D', () => ({
  default: ({ cameraRef }: { cameraRef: { current: unknown } }) => {
    cameraRef.current = cam;
    return <div data-testid="scene" />;
  },
}));

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

describe('BodyViewer3D camera controls (WCAG 2.5.7)', () => {
  beforeEach(() => Object.values(cam).forEach((f) => f.mockClear()));

  it('buttons call the camera API', async () => {
    view();
    await userEvent.click(screen.getByRole('button', { name: 'Rotate left' }));
    await userEvent.click(screen.getByRole('button', { name: 'Rotate right' }));
    await userEvent.click(screen.getByRole('button', { name: 'Zoom in' }));
    await userEvent.click(screen.getByRole('button', { name: 'Zoom out' }));
    await userEvent.click(screen.getByRole('button', { name: 'Reset view' }));
    expect(cam.rotate.mock.calls).toEqual([[-1], [1]]);
    expect(cam.zoom.mock.calls).toEqual([[1], [-1]]);
    expect(cam.reset).toHaveBeenCalledTimes(1);
  });

  it('keyboard shortcuts work from a focused control, and reset clears the selection', async () => {
    const onSelect = vi.fn();
    view(onSelect);
    await userEvent.click(screen.getByRole('button', { name: 'Heart: Severe' }));
    await userEvent.keyboard('{ArrowLeft}{ArrowRight}+-');
    expect(cam.rotate.mock.calls).toEqual([[-1], [1]]);
    expect(cam.zoom.mock.calls).toEqual([[1], [-1]]);
    await userEvent.keyboard('r');
    expect(cam.reset).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenLastCalledWith(null);
  });

  it('buttons are keyboard reachable and axe clean', async () => {
    const { container } = view();
    const first = screen.getByRole('button', { name: 'Rotate left' });
    first.focus();
    await userEvent.tab();
    expect(screen.getByRole('button', { name: 'Rotate right' })).toHaveFocus();
    expect(await axe(container)).toHaveNoViolations();
  });
});
