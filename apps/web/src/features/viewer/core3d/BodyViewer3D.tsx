'use client';

import { useTranslations } from 'next-intl';
import { useMemo, useRef, useState } from 'react';
import { dedupeRegions, keyAction, nextSelection, type CameraApi, type Region3D } from './logic';
import Scene3D from './Scene3D';

export type BodyViewer3DProps = {
  regions: Region3D[];
  model: 'body' | 'heart';
  onSelect?: (regionCode: string | null) => void;
  onLowFps?: () => void;
};

export function BodyViewer3D({ regions, model, onSelect, onLowFps }: BodyViewer3DProps) {
  const t = useTranslations('viewer3d');
  const ts = useTranslations('viewer.severity');
  const [selected, setSelected] = useState<string | null>(null);
  const list = useMemo(() => dedupeRegions(regions), [regions]);
  const listed = useMemo(() => new Set(list.map((r) => r.region_code)), [list]);

  const select = (code: string | null) => {
    const next = nextSelection(code, listed);
    setSelected(next);
    onSelect?.(next);
  };
  const current = list.find((r) => r.region_code === selected);

  const cameraRef = useRef<CameraApi | null>(null);
  const act = (a: ReturnType<typeof keyAction>) => {
    if (!a) return;
    if (a.type === 'rotate') cameraRef.current?.rotate(a.dir);
    else if (a.type === 'zoom') cameraRef.current?.zoom(a.dir);
    else {
      cameraRef.current?.reset();
      select(null);
    }
  };
  const tu = useTranslations('viewerUi.controls');
  const buttons = [
    ['rotateLeft', '↺', { type: 'rotate', dir: -1 }],
    ['rotateRight', '↻', { type: 'rotate', dir: 1 }],
    ['zoomIn', '+', { type: 'zoom', dir: 1 }],
    ['zoomOut', '−', { type: 'zoom', dir: -1 }],
    ['reset', '⟲', { type: 'reset' }],
  ] as const;

  return (
    <section
      className="max-w-3xl"
      aria-label={t('title')}
      onKeyDown={(e) => {
        if (e.key === 'Escape') return select(null);
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        const a = keyAction(e.key);
        if (a) {
          e.preventDefault();
          act(a);
        }
      }}
    >
      <div
        role="img"
        aria-label={t(`canvas.${model}`)}
        className="h-96 w-full rounded-lg bg-[var(--ml-color-brand-surface)] ring-1 ring-[var(--ml-color-brand-border)]"
      >
        <Scene3D model={model} regions={list} selected={selected} onPick={select} onLowFps={onLowFps} cameraRef={cameraRef} />
      </div>
      <div role="group" aria-label={tu('label')} className="mt-2 flex flex-wrap gap-2">
        {buttons.map(([key, glyph, a]) => (
          <button
            key={key}
            type="button"
            aria-label={tu(key)}
            title={tu(key)}
            className="min-h-target min-w-target rounded-md px-3 text-sm ring-1 ring-[var(--ml-color-brand-border)]"
            onClick={() => act(a)}
          >
            <span aria-hidden="true">{glyph}</span>
          </button>
        ))}
      </div>
      <p className="mt-1 text-xs text-[var(--ml-color-brand-textMuted)]">{tu('keys')}</p>
      <p className="mt-1 text-xs text-[var(--ml-color-brand-textMuted)]">{t('hint')}</p>

      <div aria-live="polite" className="mt-3 min-h-16 rounded-md p-3 ring-1 ring-[var(--ml-color-brand-border)]">
        {current ? (
          <>
            <h3 className="text-base font-semibold">{t('detail')}</h3>
            <p className="text-sm" data-testid="detail">{current.label}: {ts(current.severity)}</p>
            <button type="button" className="mt-2 min-h-target rounded-md px-3 text-sm ring-1 ring-[var(--ml-color-brand-border)]" onClick={() => select(null)}>
              {t('clear')}
            </button>
          </>
        ) : (
          <p className="text-sm">{t('none')}</p>
        )}
      </div>

      <h3 className="mt-3 text-base font-semibold">{t('listTitle')}</h3>
      {list.length === 0 ? (
        <p className="text-sm">{t('empty')}</p>
      ) : (
        <ul className="flex list-none flex-wrap gap-2 p-0 text-sm">
          {list.map((r) => (
            <li key={r.region_code}>
              <button
                type="button"
                aria-pressed={r.region_code === selected}
                className="min-h-target rounded-md px-3 ring-1 ring-[var(--ml-color-brand-border)] aria-pressed:bg-[var(--ml-color-brand-primary)] aria-pressed:text-white"
                onClick={() => select(r.region_code)}
              >
                {r.label}: {ts(r.severity)}
              </button>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-2 text-xs text-[var(--ml-color-brand-textMuted)]">{t('note')}</p>
    </section>
  );
}
