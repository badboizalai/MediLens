import { describe, expect, it } from 'vitest';
import { isTerminal, viewOf } from './progressView';

describe('viewOf', () => {
  it.each([
    ['uploaded', 0],
    ['classified', 1],
    ['extracted', 2],
  ])('%s is a working step', (s, step) => expect(viewOf(s)).toEqual({ kind: 'working', step }));

  it('maps terminal statuses', () => {
    expect(viewOf('needs_review')).toEqual({ kind: 'ready' });
    expect(viewOf('rejected')).toEqual({ kind: 'rejected' });
    expect(viewOf('failed')).toEqual({ kind: 'failed' });
    expect(viewOf('needs_retake', 'blurry')).toEqual({ kind: 'retake', reason: 'blurry' });
  });

  it('retake with a missing or unknown reason keeps generic guidance', () => {
    expect(viewOf('needs_retake')).toEqual({ kind: 'retake', reason: null });
    expect(viewOf('needs_retake', 'weird')).toEqual({ kind: 'retake', reason: null });
  });

  it('unknown status falls back to waiting and keeps polling', () => {
    const v = viewOf('something_new');
    expect(v).toEqual({ kind: 'working', step: 0 });
    expect(isTerminal(v)).toBe(false);
  });
});
