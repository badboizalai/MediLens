import type { SeverityKey } from '@medilens/design-system';
import type { FindingDto, ObservationDto } from '@/lib/api/findings';

export type Visit = { key: string; date: string | null; findings: FindingDto[]; observations: ObservationDto[] };

const SEVERITIES = new Set<string>(['monitor', 'mild', 'moderate', 'severe', 'spread', 'reference']);

type Dated = { document_id: string | null; observed_at: string | null };
const keyOf = (x: Dated) => x.document_id ?? x.observed_at?.slice(0, 10) ?? null;

/** One visit per document (else per calendar day); items with neither are not placeable and are dropped. Newest first. */
export function groupVisits(findings: FindingDto[], observations: ObservationDto[]): Visit[] {
  const m = new Map<string, Visit>();
  const visit = (x: Dated) => {
    const key = keyOf(x);
    if (!key) return null;
    let v = m.get(key);
    if (!v) m.set(key, (v = { key, date: null, findings: [], observations: [] }));
    if (x.observed_at && (!v.date || x.observed_at > v.date)) v.date = x.observed_at;
    return v;
  };
  for (const x of findings) visit(x)?.findings.push(x);
  for (const x of observations) visit(x)?.observations.push(x);
  return [...m.values()].sort((a, b) => (b.date ?? '').localeCompare(a.date ?? ''));
}

/** Neutral set difference by region (left = first pick, right = second pick). No ranking, no interpretation (BR-042). */
export function diffRegions(left: FindingDto[], right: FindingDto[]) {
  const l = new Set(left.map((x) => x.region_code));
  const r = new Set(right.map((x) => x.region_code));
  return {
    added: [...r].filter((c) => !l.has(c)),
    removed: [...l].filter((c) => !r.has(c)),
    both: [...r].filter((c) => l.has(c)),
  };
}

export const toRegions = (findings: FindingDto[]) =>
  findings.map((f) => ({
    region_code: f.region_code,
    severity: (f.severity && SEVERITIES.has(f.severity) ? f.severity : 'reference') as SeverityKey,
    label: f.label ?? f.region_code,
  }));

/** Side-by-side lab rows aligned on name + unit; a missing side is null. */
export function pairRows(left: ObservationDto[], right: ObservationDto[]) {
  const rows = new Map<string, { name: string; unit: string | null; left: string | null; right: string | null }>();
  const put = (list: ObservationDto[], side: 'left' | 'right') => {
    for (const x of list) {
      const k = `${x.name.toLowerCase()}|${x.unit ?? ''}`;
      const row = rows.get(k) ?? { name: x.name, unit: x.unit, left: null, right: null };
      row[side] = x.value;
      rows.set(k, row);
    }
  };
  put(left, 'left');
  put(right, 'right');
  return [...rows.values()];
}
