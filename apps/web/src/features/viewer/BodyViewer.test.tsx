// @vitest-environment jsdom
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import { axe } from 'vitest-axe';
import { describe, expect, it, vi } from 'vitest';
import en from '../../../messages/en.json';
import { BodyViewer, Boundary } from './BodyViewer';

vi.mock('./core3d/BodyViewer3DLazy', () => ({ BodyViewer3DLazy: () => <div data-testid="v3d" /> }));
vi.mock('./core/BodyMap2D', () => ({ BodyMap2D: () => <div data-testid="v2d" /> }));

const regions = [{ region_code: 'heart', severity: 'severe' as const, label: 'Heart' }];

describe('BodyViewer', () => {
  it('falls back to 2D with an announced reason when WebGL is missing, and the user can switch', async () => {
    // jsdom has no WebGL context -> noWebgl
    const { container } = render(
      <NextIntlClientProvider locale="en" messages={en}>
        <BodyViewer regions={regions} model="body" />
      </NextIntlClientProvider>,
    );
    await screen.findByTestId('v2d');
    expect(screen.getByRole('status')).toHaveTextContent(/3D is not available/);
    expect(await axe(container)).toHaveNoViolations();
    await userEvent.click(screen.getByRole('button', { name: 'Switch to 3D view' }));
    await waitFor(() => expect(screen.getByTestId('v3d')).toBeTruthy());
    expect(screen.getByRole('status')).toHaveTextContent('Showing the 3D view.');
  });
});

describe('Boundary', () => {
  it('reports a throwing child so the caller can fall back', () => {
    const onError = vi.fn();
    const Bomb = () => {
      throw new Error('webgl lost');
    };
    vi.spyOn(console, 'error').mockImplementation(() => {});
    render(
      <Boundary onError={onError}>
        <Bomb />
      </Boundary>,
    );
    expect(onError).toHaveBeenCalledTimes(1);
  });
});
