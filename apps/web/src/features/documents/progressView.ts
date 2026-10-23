import { RETAKE_REASONS, type RetakeReason } from '@/lib/api/client';

/** What the progress screen shows for a document status; copy lives under the `progress` i18n namespace. */
export type View =
  | { kind: 'working'; step: 0 | 1 | 2 }
  | { kind: 'ready' }
  | { kind: 'retake'; reason: RetakeReason | null }
  | { kind: 'rejected' }
  | { kind: 'failed' };

const WORKING: Record<string, 0 | 1 | 2> = {
  'uploaded-pending': 0,
  uploaded: 0,
  validated: 1,
  preprocessed: 1,
  classified: 1,
  ocr_done: 2,
  extracted: 2,
};

export function viewOf(status: string, retakeReason?: string | null): View {
  if (Object.hasOwn(WORKING, status)) return { kind: 'working', step: WORKING[status]! };
  if (status === 'needs_review' || status === 'confirmed') return { kind: 'ready' };
  if (status === 'needs_retake') {
    return { kind: 'retake', reason: RETAKE_REASONS.find((r) => r === retakeReason) ?? null };
  }
  if (status === 'rejected') return { kind: 'rejected' };
  if (status === 'failed') return { kind: 'failed' };
  return { kind: 'working', step: 0 }; // unknown status: keep waiting rather than show a wrong error
}

export const isTerminal = (v: View) => v.kind !== 'working';
