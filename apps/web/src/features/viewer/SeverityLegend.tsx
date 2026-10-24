'use client';

import { SeverityBadge, severityKeys } from '@medilens/design-system';
import { useLocale, useTranslations } from 'next-intl';

/** BR-020: every level is shown with symbol + word; labels come from the design-system tokens. */
export function SeverityLegend() {
  const t = useTranslations('viewerUi.legend');
  const locale = useLocale() === 'vi' ? 'vi' : 'en';
  return (
    <section aria-labelledby="sev-legend" className="my-2">
      <h3 id="sev-legend" className="text-sm font-semibold">{t('title')}</h3>
      <ul className="m-0 flex list-none flex-wrap gap-2 p-0">
        {severityKeys.map((k) => (
          <li key={k}>
            <SeverityBadge severity={k} locale={locale} />
          </li>
        ))}
      </ul>
      <p className="mt-1 text-xs text-[var(--ml-color-brand-textMuted)]">{t('hint')}</p>
    </section>
  );
}
