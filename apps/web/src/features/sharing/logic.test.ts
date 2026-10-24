import { describe, expect, it } from 'vitest';
import { statusOf, timeLeft } from './logic';

const now = Date.parse('2026-10-24T00:00:00Z');
describe('sharing logic', () => {
  it('derives status', () => {
    expect(statusOf({ expires_at: '2026-10-25T00:00:00Z', revoked_at: null }, now)).toBe('active');
    expect(statusOf({ expires_at: '2026-10-23T00:00:00Z', revoked_at: null }, now)).toBe('expired');
    expect(statusOf({ expires_at: '2026-10-25T00:00:00Z', revoked_at: '2026-10-24T00:00:00Z' }, now)).toBe('revoked');
  });
  it('formats time left', () => {
    expect(timeLeft('2026-10-24T05:30:00Z', now)).toEqual({ unit: 'hours', n: 6 });
    expect(timeLeft('2026-10-31T00:00:00Z', now)).toEqual({ unit: 'days', n: 7 });
  });
});
