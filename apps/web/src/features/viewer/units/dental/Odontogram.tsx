'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import raw from '../../../../../../../packages/anatomy-assets/svg/odontogram.svg?raw';

export type ToothState = 'caries' | 'filled' | 'missing' | 'implant';
export type Surface = 'M' | 'D' | 'O' | 'B' | 'L';
export type OdontogramTooth = {
  fdi: string;
  state: ToothState;
  /** Extraction output may also say I (incisal) or P (palatal); they are drawn as O and L. */
  surfaces?: (Surface | 'I' | 'P')[];
  label?: string;
};
export type OdontogramProps = { teeth: OdontogramTooth[] };

type Shape = {
  tag: 'polygon' | 'rect';
  id: string;
  surface: Surface;
  attrs: Record<string, string>;
};
type ToothArt = { fdi: string; transform: string; label: string; shapes: Shape[] };

const attrsOf = (s: string) =>
  Object.fromEntries([...s.matchAll(/([\w-]+)="([^"]*)"/g)].map((m) => [m[1]!, m[2]!]));

// Our own fixed-format artwork (S8-T74), so a regex is enough; shapes become React elements.
function parse(src: string): Map<string, ToothArt> {
  const out = new Map<string, ToothArt>();
  for (const g of src.matchAll(
    /<g id="tooth_(\d\d)" class="tooth" transform="([^"]*)">([\s\S]*?)<\/g>/g,
  )) {
    const shapes = [...g[3]!.matchAll(/<(polygon|rect)\s([^>]*?)\/?>/g)].map((m) => {
      const { id = '', class: _c, fill: _f, stroke: _s, ...attrs } = attrsOf(m[2]!);
      return { tag: m[1] as Shape['tag'], id, surface: id.split('__')[1] as Surface, attrs };
    });
    out.set(g[1]!, {
      fdi: g[1]!,
      transform: g[2]!,
      label: g[3]!.match(/<text[^>]*>(\d+)<\/text>/)?.[1] ?? g[1]!,
      shapes,
    });
  }
  return out;
}
const TEETH = parse(raw);
const VIEWBOX = raw.match(/viewBox="([^"]+)"/)?.[1] ?? '0 0 490 150';

const SURFACE_ALIAS: Record<string, Surface> = { I: 'O', P: 'L' };
const toSurface = (s: string): Surface | undefined => {
  const u = (SURFACE_ALIAS[s.toUpperCase()] ?? s.toUpperCase()) as Surface;
  return ['M', 'D', 'O', 'B', 'L'].includes(u) ? u : undefined;
};
const TOKEN: Record<ToothState, string> = {
  caries: 'moderate',
  filled: 'reference',
  implant: 'monitor',
  missing: 'reference',
};
// Non-colour cues (BR-020): missing = dashed outline + cross, implant = ring, caries/filled = solid fill/hatch weight.
const dash: Partial<Record<ToothState, string>> = { missing: '3 2', filled: '1 1' };

export function Odontogram({ teeth }: OdontogramProps) {
  const t = useTranslations('dental');
  const [selected, setSelected] = useState<string | null>(null);

  const byFdi = new Map<string, { state: ToothState; surfaces: Surface[]; text: string }>();
  for (const x of teeth) {
    if (!TEETH.has(x.fdi)) {
      if (process.env.NODE_ENV !== 'production')
        console.warn(`Odontogram: unknown FDI "${x.fdi}" ignored`);
      continue;
    }
    const surfaces = [
      ...new Set((x.surfaces ?? []).map(toSurface).filter((s): s is Surface => !!s)),
    ];
    const state = t(`state.${x.state}`);
    const text = surfaces.length
      ? t('itemSurfaces', {
          fdi: x.fdi,
          state,
          surfaces: surfaces.map((s) => t(`surface.${s}`)).join(', '),
        })
      : t('item', { fdi: x.fdi, state });
    byFdi.set(x.fdi, { state: x.state, surfaces, text });
  }
  const affected = [...byFdi.keys()];
  const toggle = (fdi: string) => setSelected((c) => (c === fdi ? null : fdi));

  return (
    <figure className="m-0 max-w-3xl">
      <svg
        viewBox={VIEWBOX}
        role="group"
        aria-label={t('chartLabel')}
        className="h-auto w-full text-[var(--ml-color-brand-textMuted)]"
      >
        {[...TEETH.values()].map((tooth) => {
          const info = byFdi.get(tooth.fdi);
          const sel = selected === tooth.fdi;
          const interactive = info
            ? {
                tabIndex: 0,
                role: 'button',
                'aria-pressed': sel,
                'aria-label': info.text,
                onClick: () => toggle(tooth.fdi),
                onKeyDown: (e: React.KeyboardEvent) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggle(tooth.fdi);
                  }
                },
              }
            : { 'aria-hidden': true };
          return (
            <g
              key={tooth.fdi}
              id={`tooth_${tooth.fdi}`}
              className="tooth outline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--ml-color-brand-primary)]"
              transform={tooth.transform}
              data-state={info?.state}
              {...interactive}
            >
              {tooth.shapes.map(({ tag: Tag, id, surface, attrs }) => {
                const on = info && (info.surfaces.length === 0 || info.surfaces.includes(surface));
                const state = on ? info.state : undefined;
                const Shape = Tag as 'polygon';
                return (
                  <Shape
                    key={id}
                    {...attrs}
                    id={id}
                    className={`surface surface-${surface}${sel && on ? ' is-selected' : ''}`}
                    data-state={state}
                    fill={
                      state && state !== 'missing'
                        ? `var(--ml-color-severity-${TOKEN[state]})`
                        : 'none'
                    }
                    fillOpacity={state ? 0.75 : undefined}
                    stroke="currentColor"
                    strokeWidth={sel && on ? 2 : 1}
                    strokeDasharray={state ? dash[state] : undefined}
                  />
                );
              })}
              {info?.state === 'missing' && (
                <path
                  d="M0,0 L28,28 M28,0 L0,28"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  fill="none"
                />
              )}
              {info?.state === 'implant' && (
                <circle cx={14} cy={14} r={13} fill="none" stroke="currentColor" strokeWidth={2} />
              )}
              <text x="14" y="-3" fontSize="9" textAnchor="middle" fill="currentColor">
                {tooth.label}
              </text>
            </g>
          );
        })}
      </svg>
      <figcaption>
        <h3 className="mt-3 text-base font-semibold">{t('listTitle')}</h3>
        {affected.length === 0 ? (
          <p className="text-sm">{t('empty')}</p>
        ) : (
          <ul className="list-disc pl-5 text-sm">
            {affected.map((fdi) => (
              <li key={fdi}>{byFdi.get(fdi)!.text}</li>
            ))}
          </ul>
        )}
        <p role="status" className="mt-2 text-sm font-medium">
          {selected && t('details', { text: byFdi.get(selected)!.text })}
        </p>
        <p className="mt-2 text-xs text-[var(--ml-color-brand-textMuted)]">{t('note')}</p>
      </figcaption>
    </figure>
  );
}
