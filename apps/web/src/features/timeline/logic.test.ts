import { describe, expect, it } from 'vitest';
import { diffRegions, groupVisits, pairRows, toRegions } from './logic';

const f = (region_code: string, document_id: string | null, observed_at: string | null, severity: string | null = 'mild') => ({
  region_code, laterality: null, severity, unit_code: null, is_metastasis: false, observed_at, document_id, label: null,
});
const o = (name: string, value: string, document_id: string, unit: string | null = 'mg/dL') => ({
  name, value, unit, loinc_code: null, ref_low: null, ref_high: null, observed_at: null, document_id,
});

describe('groupVisits', () => {
  it('groups by document, newest first, falls back to date, drops undated orphans', () => {
    const v = groupVisits(
      [f('liver', 'd1', '2026-01-02T00:00:00Z'), f('lung_l', 'd1', '2026-01-02T00:00:00Z'), f('heart', 'd2', '2026-03-01T00:00:00Z'),
       f('brain', null, '2025-12-01T10:00:00Z'), f('colon', null, null)],
      [o('Hb', '13', 'd2')],
    );
    expect(v.map((x) => x.key)).toEqual(['d2', 'd1', '2025-12-01']);
    expect(v[1]!.findings).toHaveLength(2);
    expect(v[0]!.observations).toHaveLength(1);
  });
});

describe('diffRegions', () => {
  it('splits into new / no longer listed / both without ranking', () => {
    const left = [f('liver', 'a', null), f('heart', 'a', null)];
    const right = [f('heart', 'b', null), f('brain', 'b', null)];
    expect(diffRegions(left, right)).toEqual({ added: ['brain'], removed: ['liver'], both: ['heart'] });
  });
});

describe('toRegions', () => {
  it('maps unknown or missing severity to reference', () => {
    const sev = toRegions([f('liver', 'a', null, null), f('heart', 'a', null, 'severe'), f('brain', 'a', null, 'x')]).map((r) => r.severity);
    expect(sev).toEqual(['reference', 'severe', 'reference']);
  });
});

describe('pairRows', () => {
  it('aligns observations by name and unit', () => {
    const rows = pairRows([o('Hb', '12', 'a'), o('Na', '140', 'a', 'mmol/L')], [o('Hb', '13', 'b')]);
    expect(rows).toEqual([
      { name: 'Hb', unit: 'mg/dL', left: '12', right: '13' },
      { name: 'Na', unit: 'mmol/L', left: '140', right: null },
    ]);
  });
});
