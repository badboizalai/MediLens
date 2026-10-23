'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { useLocale, useTranslations } from 'next-intl';
import { useState } from 'react';
import { Alert } from '@/components/ui';
import { BodyViewer } from '../viewer/BodyViewer';
import { BodyMap2D } from '../viewer/core/BodyMap2D';
import { useVisits, newClient } from './api';
import { diffRegions, pairRows, toRegions, type Visit } from './logic';

// No app-wide QueryClientProvider exists yet; the profile routes own one.
export function TimelineProviders({ profileId, view }: { profileId: string; view: 'timeline' | 'body' }) {
  const [client] = useState(newClient);
  return (
    <QueryClientProvider client={client}>
      {view === 'timeline' ? <TimelineScreen profileId={profileId} /> : <ProfileBodyScreen profileId={profileId} />}
    </QueryClientProvider>
  );
}

function useStates(profileId: string) {
  const t = useTranslations('timeline');
  const q = useVisits(profileId);
  if (q.isPending) return { node: <p role="status">{t('loading')}</p> };
  if (q.isError) return { node: <Alert tone="danger">{t('loadError')}</Alert> };
  if (q.data.length === 0) return { node: <p>{t('empty')}</p> };
  return { visits: q.data };
}

export function ProfileBodyScreen({ profileId }: { profileId: string }) {
  const t = useTranslations('timeline');
  const s = useStates(profileId);
  const date = useDate();
  if (!s.visits) return s.node;
  const latest = s.visits[0]!;
  return (
    <div className="grid gap-4">
      <p>{t('latestVisit', { date: date(latest.date) })}</p>
      <BodyViewer regions={toRegions(latest.findings)} model="body" />
    </div>
  );
}

function useDate() {
  const t = useTranslations('timeline');
  const locale = useLocale();
  return (iso: string | null) =>
    iso ? new Date(iso).toLocaleDateString(locale, { dateStyle: 'medium', timeZone: 'UTC' }) : t('undated');
}

export function TimelineScreen({ profileId }: { profileId: string }) {
  const t = useTranslations('timeline');
  const r = useTranslations('viewer');
  const s = useStates(profileId);
  const date = useDate();
  // Default: the two most recent visits, earlier on the left.
  const [pick, setPick] = useState<{ left?: string; right?: string }>({});
  if (!s.visits) return s.node;
  const visits = s.visits;
  if (visits.length < 2) {
    return (
      <div className="grid gap-2">
        <p>{t('oneVisit')}</p>
        <ProfileBodyScreen profileId={profileId} />
      </div>
    );
  }
  const find = (key: string | undefined, fallback: Visit) => visits.find((v) => v.key === key) ?? fallback;
  const left = find(pick.left, visits[1]!);
  const right = find(pick.right, visits[0]!);
  const region = (c: string) => (r.has(`regions.${c}`) ? r(`regions.${c}`) : c);
  const diff = diffRegions(left.findings, right.findings);
  const rows = pairRows(left.observations, right.observations);
  const sections = [
    ['added', diff.added],
    ['removed', diff.removed],
    ['both', diff.both],
  ] as const;

  return (
    <div className="grid gap-6">
      <div className="grid gap-3 sm:grid-cols-2">
        {(['left', 'right'] as const).map((side) => (
          <label key={side} className="grid gap-1 text-sm font-medium">
            {t(side === 'left' ? 'pickBefore' : 'pickAfter')}
            <select
              className="min-h-target rounded-md px-2 ring-1 ring-[var(--ml-color-brand-border)]"
              value={(side === 'left' ? left : right).key}
              onChange={(e) => setPick((p) => ({ ...p, [side]: e.target.value }))}
            >
              {visits.map((v) => <option key={v.key} value={v.key}>{date(v.date)}</option>)}
            </select>
          </label>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {[left, right].map((v, i) => (
          <section key={i} aria-labelledby={`visit-${i}`} className="grid content-start gap-2">
            <h2 id={`visit-${i}`} className="text-lg font-semibold">{t(i === 0 ? 'before' : 'after')}</h2>
            <BodyMap2D findings={toRegions(v.findings)} side="front" />
          </section>
        ))}
      </div>

      <section aria-labelledby="tl-diff" className="grid gap-3">
        <h2 id="tl-diff" className="text-lg font-semibold">{t('diffTitle')}</h2>
        <p className="text-sm text-[var(--ml-color-brand-textMuted)]">{t('diffNote')}</p>
        {sections.map(([k, codes]) => (
          <div key={k}>
            <h3 className="font-medium">{t(`diff.${k}`)}</h3>
            {codes.length ? (
              <ul className="list-disc pl-5">{codes.map((c) => <li key={c}>{region(c)}</li>)}</ul>
            ) : (
              <p className="text-sm">{t('none')}</p>
            )}
          </div>
        ))}
      </section>

      <section aria-labelledby="tl-obs" className="grid gap-2">
        <h2 id="tl-obs" className="text-lg font-semibold">{t('obsTitle')}</h2>
        {rows.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">{t('obsCaption')}</caption>
              <thead>
                <tr>
                  <th scope="col" className="p-2">{t('obsName')}</th>
                  <th scope="col" className="p-2">{t('before')}</th>
                  <th scope="col" className="p-2">{t('after')}</th>
                  <th scope="col" className="p-2">{t('obsUnit')}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((x) => (
                  <tr key={`${x.name}|${x.unit}`} className="border-t border-[var(--ml-color-brand-border)]">
                    <th scope="row" className="p-2 font-normal">{x.name}</th>
                    <td className="p-2">{x.left ?? t('notListed')}</td>
                    <td className="p-2">{x.right ?? t('notListed')}</td>
                    <td className="p-2">{x.unit ?? ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm">{t('none')}</p>
        )}
      </section>
    </div>
  );
}
