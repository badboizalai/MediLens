'use client';

import type { SeverityKey } from '@medilens/design-system';
import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import { BODY, type Side } from './parseBodySvg';

export type Finding = {
  region_code: string;
  severity: SeverityKey;
  /** `patient_reported` is drawn neutral with no severity (BR-040). */
  source?: string | null;
  /** Drawn with the neutral spread style and the text "stated in your record" (BR-049, copy pending CSO). */
  is_metastasis?: boolean;
  label?: string | null;
};
type Kind = SeverityKey | 'reported';
export type BodyMap2DProps = {
  findings: Finding[];
  side: Side;
  /** Codes that exist on neither body side; not drawn, but listed as "not placed on the body" (HZ-002). */
  onUnknownRegion?: (codes: string[]) => void;
};

// Higher wins when one region has several findings, so the map never understates what was noted.
const RANK: Record<Kind, number> = { reported: -1, reference: 0, monitor: 1, mild: 2, moderate: 3, severe: 4, spread: 5 };
const KNOWN = new Set([...BODY.front.regions, ...BODY.back.regions].map((r) => r.id));
// Non-colour cue (WCAG 1.4.1): findings get a heavier outline, spread/reference a dashed one.
const dash = (s: Kind) => (s === 'spread' ? '6 3' : s === 'reference' ? '2 2' : undefined);

export function BodyMap2D({ findings, side, onUnknownRegion }: BodyMap2DProps) {
  const t = useTranslations('viewer');
  const [active, setActive] = useState<string | null>(null);

  const n = useTranslations('viewerNotes');
  const bySeverity = new Map<string, Kind>();
  const stated = new Set<string>();
  const unknown: string[] = [];
  const unmapped: Finding[] = [];
  for (const f of findings) {
    if (!KNOWN.has(f.region_code)) {
      unmapped.push(f);
      if (!unknown.includes(f.region_code)) unknown.push(f.region_code);
      continue;
    }
    const reported = f.source === 'patient_reported';
    const kind: Kind = reported ? 'reported' : f.is_metastasis ? 'spread' : f.severity;
    const cur = bySeverity.get(f.region_code);
    if (!cur || RANK[kind] > RANK[cur]) bySeverity.set(f.region_code, kind);
    if (f.is_metastasis && !reported) stated.add(f.region_code);
  }
  const unknownKey = unknown.join(',');
  useEffect(() => {
    if (unknownKey) onUnknownRegion?.(unknownKey.split(','));
  }, [unknownKey, onUnknownRegion]);

  const label = (code: string) => {
    const k = bySeverity.get(code)!;
    const base = t('item', { region: t(`regions.${code}`), severity: k === 'reported' ? n('patientReported') : t(`severity.${k}`) });
    return k === 'spread' && stated.has(code) ? `${base}, ${n('statedInRecord')}` : base;
  };
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
                style={{ fill: sev === 'reported' ? 'var(--ml-color-brand-surfaceMuted)' : `var(--ml-color-severity-${sev})`, fillOpacity: sev === 'reported' ? 1 : 0.75, stroke: 'currentColor', strokeWidth: 2, strokeDasharray: dash(sev) }}
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
        {unmapped.length > 0 && (
          <section aria-labelledby="unmapped-title">
            <h3 id="unmapped-title" className="mt-3 text-base font-semibold">{n('unmapped')}</h3>
            <p className="text-xs text-[var(--ml-color-brand-textMuted)]">{n('unmappedHint')}</p>
            <ul className="list-disc pl-5 text-sm">
              {unmapped.map((f, i) => (
                <li key={i}>{f.label ?? f.region_code}{f.source === 'patient_reported' ? ` (${n('patientReported')})` : ''}</li>
              ))}
            </ul>
          </section>
        )}
        <p className="mt-2 text-xs text-[var(--ml-color-brand-textMuted)]">{t('note')}</p>
      </figcaption>
    </figure>
  );
}

const findingsOnList = (m: Map<string, Kind>) => [...m.keys()];
