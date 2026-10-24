import { tokens, type SeverityKey } from '@medilens/design-system';

export type Region3D = { region_code: string; severity: SeverityKey; label: string };

/** Mesh/node name -> region_code; coarser `__lod1` copies resolve to the same region. */
export const regionOf = (meshName: string) => meshName.replace(/__lod1$/, '');
export const isLod1 = (meshName: string) => meshName.endsWith('__lod1');

export const NEUTRAL_COLOR = '#C9D1D9';
// Three.js needs literal colours, so read the light-theme hex of the design token.
export const severityColor = (s: SeverityKey) => tokens.color.severity[s].light;

// Higher wins when a region is listed twice, so the model never understates what was noted.
const RANK: Record<SeverityKey, number> = { reference: 0, monitor: 1, mild: 2, moderate: 3, severe: 4, spread: 5 };
export function dedupeRegions(regions: Region3D[]): Region3D[] {
  const m = new Map<string, Region3D>();
  for (const r of regions) {
    const cur = m.get(r.region_code);
    if (!cur || RANK[r.severity] > RANK[cur.severity]) m.set(r.region_code, r);
  }
  return [...m.values()];
}

/** Camera actions behind the on-screen buttons and keyboard shortcuts (WCAG 2.5.7). */
export type CameraApi = { rotate: (dir: -1 | 1) => void; zoom: (dir: -1 | 1) => void; reset: () => void };

/** Key to camera action; null for keys we do not handle. */
export function keyAction(key: string): { type: 'rotate' | 'zoom'; dir: -1 | 1 } | { type: 'reset' } | null {
  if (key === 'ArrowLeft') return { type: 'rotate', dir: -1 };
  if (key === 'ArrowRight') return { type: 'rotate', dir: 1 };
  if (key === '+' || key === '=') return { type: 'zoom', dir: 1 };
  if (key === '-') return { type: 'zoom', dir: -1 };
  if (key === 'r' || key === 'R') return { type: 'reset' };
  return null;
}

/** Picking an unlisted region (or nothing) clears the selection. */
export const nextSelection = (picked: string | null, listed: ReadonlySet<string>) =>
  picked && listed.has(picked) ? picked : null;
