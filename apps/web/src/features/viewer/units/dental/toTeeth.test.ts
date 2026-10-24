import { describe, expect, it } from 'vitest';
import type { FindingDto } from '@/lib/api/findings';
import { toTeeth } from './toTeeth';

const f = (region_code: string, label: string | null = null): FindingDto => ({
  region_code, label, laterality: null, severity: null, unit_code: null, is_metastasis: false,
  observed_at: null, document_id: null,
});

describe('toTeeth', () => {
  it('maps tooth_NN to FDI and ignores non-dental findings', () => {
    expect(toTeeth([f('tooth_16', 'Caries'), f('heart'), f('tooth_x1'), f('tooth_36', 'Missing tooth')])).toEqual([
      { fdi: '16', state: 'caries', label: 'Caries' },
      { fdi: '36', state: 'missing', label: 'Missing tooth' },
    ]);
  });

  it('reads filled and implant from the label', () => {
    expect(toTeeth([f('tooth_11', 'Filling'), f('tooth_21', 'Implant')]).map((t) => t.state)).toEqual(['filled', 'implant']);
  });
});
