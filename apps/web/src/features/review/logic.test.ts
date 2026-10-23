import { describe, expect, it } from 'vitest';
import type { Field } from './api';
import { canConfirm, pending } from './logic';

const f = (o: Partial<Field>): Field => ({
  id: '1', field_path: 'a', value: 'x', user_value: null, confidence: 0.9, source_page: 1,
  needs_confirmation: false, confirmed_at: null, ...o,
});

describe('review gate', () => {
  it('blocks while a low-confidence field is unconfirmed', () => {
    const fields = [f({ id: 'a' }), f({ id: 'b', confidence: 0.5, needs_confirmation: true })];
    expect(pending(fields).map((x) => x.id)).toEqual(['b']);
    expect(canConfirm(fields)).toBe(false);
  });
  it('allows once confirmed, and never on an empty list', () => {
    expect(canConfirm([f({ needs_confirmation: true, confirmed_at: '2026-01-01T00:00:00Z' })])).toBe(true);
    expect(canConfirm([])).toBe(false);
  });
});
