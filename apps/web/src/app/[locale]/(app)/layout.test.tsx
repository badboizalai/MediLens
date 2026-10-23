import { beforeEach, describe, expect, it, vi } from 'vitest';

const { auth, redirect } = vi.hoisted(() => ({
  auth: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`REDIRECT:${url}`);
  }),
}));
vi.mock('@/lib/auth', () => ({ auth }));
vi.mock('next/navigation', () => ({ redirect }));

import AppLayout from './layout';

const params = Promise.resolve({ locale: 'en' });

describe('(app) layout', () => {
  beforeEach(() => vi.clearAllMocks());

  it('redirects to sign-in without a session', async () => {
    auth.mockResolvedValue(null);
    await expect(AppLayout({ children: null, params })).rejects.toThrow('REDIRECT:/en/sign-in');
  });

  it('renders children with a session', async () => {
    auth.mockResolvedValue({ user: { name: 'x' } });
    await AppLayout({ children: 'ok', params });
    expect(redirect).not.toHaveBeenCalled();
  });
});
