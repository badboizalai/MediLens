// features/viewer/units/<unit>/index.tsx — template for a Unit plugin
import dynamic from 'next/dynamic';
import { useTranslations } from 'next-intl';
import type { Finding, UnitConfig, UnitPlugin } from '../../types';
import { SeverityChip, DisclaimerBar, SourceBadge } from '@/components/ui';

const Viewer3D = dynamic(() => import('./Viewer3D'), { ssr: false });

function Viewer2D({ config, findings, selected, onSelect }: {
  config: UnitConfig; findings: Finding[]; selected?: string; onSelect(code: string): void;
}) {
  const byRegion = new Map(findings.filter(f => f.regionCode !== 'unmapped').map(f => [f.regionCode, f]));
  return (
    <svg viewBox="0 0 400 600" role="img" aria-label={config.names.vi}>
      {config.regions.map(r => {
        const f = byRegion.get(r.regionCode);
        return (
          <path
            key={r.regionCode}
            id={r.svgId ?? r.regionCode}
            d={/* path data loaded from the unit SVG asset */ ''}
            className={f ? `severity-${f.severity ?? 'monitor'}` : 'region-default'}
            data-selected={selected === r.regionCode || undefined}
            onClick={() => onSelect(r.regionCode)}
          />
        );
      })}
    </svg>
  );
}

function Legend({ findings }: { findings: Finding[] }) {
  const t = useTranslations('viewer');
  const levels = Array.from(new Set(findings.map(f => f.severity).filter(Boolean)));
  return (
    <ul aria-label={t('legend')}>
      {levels.map(l => <li key={l!}><SeverityChip level={l!} /></li>)}
    </ul>
  );
}

function DetailPanel({ regionCode, findings, config }: { regionCode: string; findings: Finding[]; config: UnitConfig }) {
  const t = useTranslations('finding');
  const region = config.regions.find(r => r.regionCode === regionCode);
  const items = findings.filter(f => f.regionCode === regionCode);
  return (
    <section aria-labelledby="detail-title">
      <h2 id="detail-title">{region?.names.vi}</h2>
      {items.map(f => (
        <article key={f.id}>
          <SeverityChip level={f.severity ?? 'monitor'} />
          <p><strong>{t('recordSays')}</strong> “{f.sourceQuote}”</p>
          <SourceBadge findingId={f.id} />
        </article>
      ))}
      <DisclaimerBar />
    </section>
  );
}

export const plugin: UnitPlugin = {
  unitCode: '<unit>',
  Viewer2D,
  Viewer3D,
  Legend,
  DetailPanel,
  assets: { glbUrl: undefined },
};
