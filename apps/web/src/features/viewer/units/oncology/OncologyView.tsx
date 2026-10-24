'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { BodyMap2D, type Finding } from '../../core/BodyMap2D';

export type OncologyViewProps = {
  findings: Finding[];
  /** Stage as written in the record; shown verbatim (BR-048). */
  tnm?: string | null;
};

/**
 * BR-046: summary first. Metastasis findings are not even passed to the map until "Show details".
 * The toggle is local state: it resets for every record and is never persisted (BR-046).
 * Copy under `oncology.*` is a draft pending CSO review (BR-046..051).
 */
export function OncologyView({ findings, tnm }: OncologyViewProps) {
  const t = useTranslations('oncology');
  const [details, setDetails] = useState(false);
  const shown = details ? findings : findings.filter((f) => !f.is_metastasis);

  return (
    <section aria-labelledby="onco-title">
      <h2 id="onco-title" className="text-lg font-semibold">{t('title')}</h2>
      {!details && <p className="text-sm">{t('summaryNote')}</p>}
      <button
        type="button"
        aria-expanded={details}
        aria-controls="onco-details"
        className="my-2 min-h-target rounded-md px-3 text-sm ring-1 ring-[var(--ml-color-brand-border)]"
        onClick={() => setDetails((d) => !d)}
      >
        {t(details ? 'hideDetails' : 'showDetails')}
      </button>
      <BodyMap2D findings={shown} side="front" />
      {details && (
        <div id="onco-details">
          <h3 className="mt-3 text-base font-semibold">{t('detailsTitle')}</h3>
          {tnm && (
            <>
              <p className="text-sm">{t('tnmTitle')}: <strong>{tnm}</strong></p>
              <p className="text-sm">{t('tnmLetters')}</p>
              <p className="text-xs text-[var(--ml-color-brand-textMuted)]">{t('tnmNote')}</p>
            </>
          )}
          <p className="mt-2 text-sm">{t('askCareTeam')}</p>
        </div>
      )}
    </section>
  );
}
