import type { FindingDto } from '@/lib/api/findings';
import type { OdontogramTooth, ToothState } from './Odontogram';

const TOOTH = /^tooth_(\d\d)$/;

// shortcut: findings carry no tooth state, so read it from the label; replace when the API gives a state.
// An unrecognised label is not drawn: showing a state the record did not state is a safety hazard.
const stateOf = (label: string | null): ToothState | null => {
  const l = (label ?? '').toLowerCase();
  if (/missing|extract|absent|mất|nhổ/.test(l)) return 'missing';
  if (/implant|cấy ghép/.test(l)) return 'implant';
  if (/fill|restor|trám/.test(l)) return 'filled';
  if (/caries|decay|sâu/.test(l)) return 'caries';
  return null;
};

/** tooth_NN findings become odontogram teeth (NN is the FDI number); everything else is ignored. */
export const toTeeth = (findings: FindingDto[]): OdontogramTooth[] =>
  findings.flatMap((f) => {
    const m = TOOTH.exec(f.region_code);
    const state = m ? stateOf(f.label) : null;
    return m && state ? [{ fdi: m[1]!, state, label: f.label ?? undefined }] : [];
  });
