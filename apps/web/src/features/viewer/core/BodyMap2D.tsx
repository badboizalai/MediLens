'use client';

import type { SeverityKey } from '@medilens/design-system';
import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import { BODY, type Side } from './parseBodySvg';

export type Finding = { region_code: string; severity: SeverityKey };
export type BodyMap2DProps = {
  findings: Finding[];
  side: Side;
  /** Codes that exist on neither body side; they are not drawn or listed. */
  onUnknownRegion?: (codes: string[]) => void;
};

// Higher wins when one region has several findings, so the map never understates what was noted.
const RANK: Record<SeverityKey, number> = { reference: 0, monitor: 1, mild: 2, moderate: 3, severe: 4, spread: 5 };
const KNOWN = new Set([...BODY.front.regions, ...BODY.back.regions].map((r) => r.id));
// Non-colour cue (WCAG 1.4.1): findings get a heavier outline, spread/reference a dashed one.
const dash = (s: SeverityKey) => (s === 'spread' ? '6 3' : s === 'reference' ? '2 2' : undefined);

export function BodyMap2D({ findings, side, onUnknownRegion }: BodyMap2DProps) {
  const t = useTranslations('viewer');
  const [active, setActive] = useState<string | null>(null);

  const bySeverity = new Map<string, SeverityKey>();
  const unknown: string[] = [];
  for (const f of findings) {
    if (!KNOWN.has(f.region_code)) {
      if (!unknown.includes(f.region_code)) unknown.push(f.region_code);
      continue;
    }
    const cur = bySeverity.get(f.region_code);
    if (!cur || RANK[f.severity] > RANK[cur]) bySeverity.set(f.region_code, f.severity);
  }
  const unknownKey = unknown.join(',');
  useEffect(() => {
    if (unknownKey) onUnknownRegion?.(unknownKey.split(','));
  }, [unknownKey, onUnknownRegion]);

  const label = (code: string) => t('item', { region: t(`regions.${code}`), severity: t(`severity.${bySeverity.get(code)!}`) });
  const { viewBox, silhouette, regions } = BODY[side];

  return (
    <figure className="relative m-0 max-w-xs">
      <svg viewBox={viewBox} role="group" aria-label={t(side)} className="h-auto w-full text-[var(--ml-color-brand-textMuted)]">
        <g fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
          {silhouette.map((s, i) => <path key={i} d={s.attrs.d} />)}
        </g>
        <g stroke="currentColor" strokeWidth={0.75}>
          {regions.map(({ id, tag: Tag, attrs }) => {
            const sev = id ? bySeverity.get(id) : undefined;
            if (!id || !sev) return <Tag key={id} {...attrs} fill="none" aria-hidden="true" />;
            return (
              <Tag
                key={id}
                {...attrs}
                data-region={id}
                data-severity={sev}
                tabIndex={0}
                role="img"
                aria-label={label(id)}
                style={{ fill: `var(--ml-color-severity-${sev})`, fillOpacity: 0.75, stroke: 'currentColor', strokeWidth: 2, strokeDasharray: dash(sev) }}
                className="outline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--ml-color-brand-primary)]"
                onMouseEnter={() => setActive(id)}
                onMouseLeave={() => setActive(null)}
                onFocus={() => setActive(id)}
                onBlur={() => setActive(null)}
              />
            );
          })}
        </g>
      </svg>
      {active && bySeverity.has(active) && (
        <div role="tooltip" className="absolute left-0 top-0 rounded-md bg-[var(--ml-color-brand-surface)] px-3 py-1 text-sm shadow ring-1 ring-[var(--ml-color-brand-border)]">
          {label(active)}
        </div>
      )}
      <figcaption>
        <h3 className="mt-3 text-base font-semibold">{t('listTitle')}</h3>
        {findingsOnList(bySeverity).length === 0 ? (
          <p className="text-sm">{t('empty')}</p>
        ) : (
          <ul className="list-disc pl-5 text-sm">
            {findingsOnList(bySeverity).map((code) => <li key={code}>{label(code)}</li>)}
          </ul>
        )}
        <p className="mt-2 text-xs text-[var(--ml-color-brand-textMuted)]">{t('note')}</p>
      </figcaption>
    </figure>
  );
}

const findingsOnList = (m: Map<string, SeverityKey>) => [...m.keys()];
