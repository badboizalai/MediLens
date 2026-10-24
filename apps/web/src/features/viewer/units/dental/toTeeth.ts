import type { FindingDto } from '@/lib/api/findings';
import type { OdontogramTooth, ToothState } from './Odontogram';

const TOOTH = /^tooth_(\d\d)$/;

// shortcut: findings carry no tooth state, so read it from the label; default caries, replace when the API gives a state.
const stateOf = (label: string | null): ToothState => {
  const l = (label ?? '').toLowerCase();
  if (/missing|extract|absent|mất|nhổ/.test(l)) return 'missing';
  if (/implant|cấy ghép/.test(l)) return 'implant';
  if (/fill|restor|trám/.test(l)) return 'filled';
  return 'caries';
};

/** tooth_NN findings become odontogram teeth (NN is the FDI number); everything else is ignored. */
export const toTeeth = (findings: FindingDto[]): OdontogramTooth[] =>
  findings.flatMap((f) => {
    const m = TOOTH.exec(f.region_code);
    return m ? [{ fdi: m[1]!, state: stateOf(f.label), label: f.label ?? undefined }] : [];
  });
