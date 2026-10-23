import { describe, expect, it } from 'vitest';
import { dedupeRegions, isLod1, nextSelection, regionOf, severityColor } from './logic';

describe('core3d logic', () => {
  it('strips the LOD suffix', () => {
    expect(regionOf('lung_l__lod1')).toBe('lung_l');
    expect(regionOf('lung_l')).toBe('lung_l');
    expect(isLod1('heart__lod1')).toBe(true);
    expect(isLod1('heart')).toBe(false);
  });
  it('maps severity to the design-token colour', () => {
    expect(severityColor('severe')).toMatch(/^#[0-9a-f]{6}$/i);
    expect(severityColor('severe')).not.toBe(severityColor('mild'));
  });
  it('keeps the highest severity per region', () => {
    const r = dedupeRegions([
      { region_code: 'heart', severity: 'mild', label: 'Heart' },
      { region_code: 'heart', severity: 'spread', label: 'Heart' },
    ]);
    expect(r).toHaveLength(1);
    expect(r[0]!.severity).toBe('spread');
  });
  it('selects only listed regions', () => {
    const listed = new Set(['heart']);
    expect(nextSelection('heart', listed)).toBe('heart');
    expect(nextSelection('liver', listed)).toBeNull();
    expect(nextSelection(null, listed)).toBeNull();
  });
});
