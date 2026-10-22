# Unit Plugin Contract

```ts
export interface UnitConfig {
  unitCode: string;            // "dental"
  version: string;
  names: { vi: string; en: string };
  regions: Array<{ regionCode: string; meshId?: string; svgId?: string; laterality: 'left'|'right'|'midline'; names: { vi: string; en: string } }>;
  visualRules: { severityOpacity: number; marker: 'fill'|'point'|'line' };
}

export interface Finding {
  id: string; regionCode: string | 'unmapped'; severity: 'monitor'|'mild'|'moderate'|'severe'|null;
  isMetastasis: boolean; observedAt: string | null; label: { vi: string; en: string }; sourceQuote: string;
}

export interface UnitPlugin {
  unitCode: string;
  Viewer2D: React.ComponentType<{ config: UnitConfig; findings: Finding[]; selected?: string; onSelect(regionCode: string): void }>;
  Viewer3D?: React.ComponentType<{ config: UnitConfig; findings: Finding[]; selected?: string; onSelect(regionCode: string): void }>;
  Legend: React.ComponentType<{ findings: Finding[] }>;
  DetailPanel: React.ComponentType<{ regionCode: string; findings: Finding[]; config: UnitConfig }>;
  assets: { glbUrl?: string; svgComponent?: () => Promise<{ default: React.ComponentType }> };
}
```

## Registration
```ts
// features/viewer/registry.ts
const plugins = new Map<string, () => Promise<UnitPlugin>>([
  ['dental', () => import('./units/dental').then(m => m.plugin)],
  ['cardiology', () => import('./units/cardiology').then(m => m.plugin)],
  ['oncology', () => import('./units/oncology').then(m => m.plugin)],
]);
export const loadPlugin = (code: string) => plugins.get(code)?.() ?? import('./units/generic').then(m => m.plugin);
```
A Unit without a custom plugin uses the generic body plugin driven entirely by config (NFR-12).

## Rules
- Plugins never fetch data themselves; they receive config + findings.
- Plugins use tokens for colours and the shared `SeverityChip`, `DisclaimerBar`, `SourceBadge`.
- Each plugin ships Storybook stories with synthetic findings and Playwright screenshot baselines.
