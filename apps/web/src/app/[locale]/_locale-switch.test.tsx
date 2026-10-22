import { describe, expect, it, vi } from 'vitest';

vi.mock('next/navigation', () => ({ usePathname: () => '/vi/dashboard' }));

import { LocaleSwitch } from './_locale-switch';

type El = { props: { href?: string; 'aria-current'?: string; children?: unknown } };

function links(): El[] {
  const ul = LocaleSwitch({ label: 'Language' }) as unknown as { props: { children: El[] } };
  return ul.props.children.map((li) => (li as unknown as { props: { children: El } }).props.children);
}

describe('LocaleSwitch', () => {
  it('keeps the current path when switching locale', () => {
    expect(links().map((a) => a.props.href)).toEqual(['/vi/dashboard', '/en/dashboard']);
  });

  it('marks the current locale', () => {
    const [vi_, en] = links();
    expect(vi_.props['aria-current']).toBe('true');
    expect(en.props['aria-current']).toBeUndefined();
  });
});
