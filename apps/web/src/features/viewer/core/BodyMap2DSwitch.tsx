'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { BodyMap2D, type BodyMap2DProps } from './BodyMap2D';

/** Front/back toggle around BodyMap2D; the findings list is side-independent so it is kept. */
export function BodyMap2DSwitch(props: Omit<BodyMap2DProps, 'side'>) {
  const t = useTranslations('viewerUi.side');
  const [side, setSide] = useState<'front' | 'back'>('front');
  return (
    <div>
      <div role="group" aria-label={t('label')} className="mb-2 flex gap-2">
        {(['front', 'back'] as const).map((s) => (
          <button
            key={s}
            type="button"
            aria-pressed={side === s}
            className="min-h-target rounded-md px-3 text-sm ring-1 ring-[var(--ml-color-brand-border)] aria-pressed:bg-[var(--ml-color-brand-primary)] aria-pressed:text-white"
            onClick={() => setSide(s)}
          >
            {t(s)}
          </button>
        ))}
      </div>
      <BodyMap2D {...props} side={side} />
    </div>
  );
}
