'use client';

import { useTranslations } from 'next-intl';
import { Component, useEffect, useState, type ReactNode } from 'react';
import { BodyMap2D } from './core/BodyMap2D';
import { decideViewer, detectCapabilities } from './core3d/budget';
import { BodyViewer3DLazy } from './core3d/BodyViewer3DLazy';
import type { Region3D } from './core3d/logic';

export type BodyViewerProps = {
  regions: Region3D[];
  model: 'body' | 'heart';
  onSelect?: (regionCode: string | null) => void;
};
type Reason = 'ok' | 'noWebgl' | 'saveData' | 'lowCores' | 'lowMemory' | 'lowFps' | 'error' | 'manual2d' | 'manual3d';
type State = { mode: '3d' | '2d' | null; reason: Reason; manual: boolean };

/** GLB load failures and WebGL context loss surface as render errors; fall back instead of a blank page. */
export class Boundary extends Component<{ onError: () => void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onError();
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

export function BodyViewer({ regions, model, onSelect }: BodyViewerProps) {
  const t = useTranslations('viewer3d');
  // Decided after mount: capabilities need the browser, and SSR has none.
  const [state, setState] = useState<State>({ mode: null, reason: 'ok', manual: false });
  useEffect(() => setState({ ...decideViewer(detectCapabilities()), manual: false }), []);

  if (!state.mode) return <p role="status" className="text-sm">{t('loading')}</p>;
  const to = (mode: '3d' | '2d') => setState({ mode, reason: mode === '3d' ? 'manual3d' : 'manual2d', manual: true });
  const auto2d = (reason: Reason) => setState((s) => ({ ...s, mode: '2d', reason }));

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="min-h-target rounded-md px-3 text-sm ring-1 ring-[var(--ml-color-brand-border)]"
          onClick={() => to(state.mode === '3d' ? '2d' : '3d')}
        >
          {t(state.mode === '3d' ? 'switchTo2d' : 'switchTo3d')}
        </button>
        <p role="status" className="text-xs text-[var(--ml-color-brand-textMuted)]">
          {state.reason === 'ok' ? '' : t(`reason.${state.reason}`)}
        </p>
      </div>
      {state.mode === '3d' ? (
        <Boundary onError={() => auto2d('error')}>
          <BodyViewer3DLazy regions={regions} model={model} onSelect={onSelect} onLowFps={state.manual ? undefined : () => auto2d('lowFps')} />
        </Boundary>
      ) : (
        <BodyMap2D findings={regions} side="front" />
      )}
    </div>
  );
}
