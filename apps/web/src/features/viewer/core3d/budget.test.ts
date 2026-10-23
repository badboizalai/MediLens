import { describe, expect, it } from 'vitest';
import { decideViewer } from './budget';

const ok = { webgl: true, saveData: false, cores: 8, memoryGb: 8 };
describe('decideViewer', () => {
  it('uses 3D on a capable device', () => expect(decideViewer(ok)).toEqual({ mode: '3d', reason: 'ok' }));
  it('uses 3D when cores/memory are unknown', () =>
    expect(decideViewer({ webgl: true, saveData: false }).mode).toBe('3d'));
  it.each([
    [{ ...ok, webgl: false }, 'noWebgl'],
    [{ ...ok, saveData: true }, 'saveData'],
    [{ ...ok, cores: 2 }, 'lowCores'],
    [{ ...ok, memoryGb: 2 }, 'lowMemory'],
  ])('falls back to 2D %#', (c, reason) => expect(decideViewer(c)).toEqual({ mode: '2d', reason }));
});
