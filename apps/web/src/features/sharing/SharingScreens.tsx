'use client';

import { QueryClientProvider, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocale, useTranslations } from 'next-intl';
import { useState, type FormEvent } from 'react';
import { Alert, Button } from '@/components/ui';
import { ApiError } from '@/lib/api/client';
import { createShare, getMe, getSharedFindings, getSharedShare, listShares, revokeShare } from '@/lib/api/shares';
import { newClient } from '../timeline/api';
import { BodyViewer } from '../viewer/BodyViewer';
import { EXPIRY_HOURS, shortId, statusOf, timeLeft, toRegions } from './logic';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const field = 'min-h-target rounded-md px-2 ring-1 ring-[var(--ml-color-brand-border)]';

// No app-wide QueryClientProvider exists yet; these routes own one.
export function SharingProviders(props: { mode: 'owner'; profileId: string } | { mode: 'shared'; shareId: string }) {
  const [client] = useState(newClient);
  return (
    <QueryClientProvider client={client}>
      {props.mode === 'owner' ? <ShareSettings profileId={props.profileId} /> : <SharedView shareId={props.shareId} />}
    </QueryClientProvider>
  );
}

export function ShareSettings({ profileId }: { profileId: string }) {
  const t = useTranslations('sharing');
  const locale = useLocale();
  const qc = useQueryClient();
  const key = ['shares', profileId];
  const list = useQuery({ queryKey: key, queryFn: () => listShares(profileId) });
  const [grantee, setGrantee] = useState('');
  const [hours, setHours] = useState<number>(168);
  const [invalid, setInvalid] = useState(false);
  const [confirming, setConfirming] = useState<string | null>(null);
  const create = useMutation({
    mutationFn: () => createShare(profileId, grantee.trim(), hours),
    onSuccess: () => {
      setGrantee('');
      void qc.invalidateQueries({ queryKey: key });
    },
  });
  const revoke = useMutation({
    mutationFn: revokeShare,
    onSuccess: () => {
      setConfirming(null);
      void qc.invalidateQueries({ queryKey: key });
    },
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const ok = UUID.test(grantee.trim());
    setInvalid(!ok);
    if (ok) create.mutate();
  };
  const hoursLabel = (h: number) => (h < 24 ? t('hours', { n: h }) : t('days', { n: h / 24 }));
  const left = (iso: string) => {
    const x = timeLeft(iso);
    return t(x.unit === 'days' ? 'daysLeft' : 'hoursLeft', { n: x.n });
  };

  return (
    <div className="grid gap-6">
      <form onSubmit={submit} className="grid max-w-md gap-3" noValidate>
        <h2 className="text-lg font-semibold">{t('newShare')}</h2>
        <label className="grid gap-1 text-sm font-medium">
          {t('grantee')}
          <input
            className={field}
            value={grantee}
            onChange={(e) => setGrantee(e.target.value)}
            aria-invalid={invalid}
            aria-describedby={invalid ? 'grantee-err' : 'grantee-help'}
            autoComplete="off"
          />
        </label>
        <p id="grantee-help" className="text-xs text-[var(--ml-color-brand-textMuted)]">{t('granteeHelp')}</p>
        {invalid && <p id="grantee-err" role="alert" className="text-sm">{t('invalid')}</p>}
        <p className="text-sm"><span className="font-medium">{t('scope')}</span>: {t('scopeValue')}</p>
        <label className="grid gap-1 text-sm font-medium">
          {t('expiry')}
          <select className={field} value={hours} onChange={(e) => setHours(Number(e.target.value))}>
            {EXPIRY_HOURS.map((h) => <option key={h} value={h}>{hoursLabel(h)}</option>)}
          </select>
        </label>
        <p className="text-sm">{t('autoEnd')}</p>
        <Button type="submit" disabled={create.isPending}>{create.isPending ? t('creating') : t('create')}</Button>
        <div aria-live="polite">
          {create.isSuccess && <Alert tone="success">{t('created')}</Alert>}
          {create.isError && <Alert tone="danger">{create.error instanceof ApiError && create.error.status === 404 ? t('needAccount') : t('error')}</Alert>}
        </div>
      </form>

      <section aria-labelledby="share-list" className="grid gap-2">
        <h2 id="share-list" className="text-lg font-semibold">{t('listTitle')}</h2>
        {list.isPending && <p role="status">{t('loading')}</p>}
        {list.isError && <Alert tone="danger">{t('error')}</Alert>}
        {list.data?.length === 0 && <p>{t('empty')}</p>}
        {revoke.isError && <Alert tone="danger">{t('error')}</Alert>}
        <ul className="grid gap-3">
          {list.data?.map((s) => {
            const st = statusOf(s);
            const who = shortId(s.grantee_user_id);
            return (
              <li key={s.id} className="grid gap-1 rounded-md p-3 ring-1 ring-[var(--ml-color-brand-border)]">
                <p className="font-medium">{t('recipient', { id: who })}</p>
                <p className="text-sm">
                  {t(`status.${st}`)}
                  {' · '}
                  {st === 'active' ? left(s.expires_at) : new Date(s.revoked_at ?? s.expires_at).toLocaleString(locale)}
                </p>
                {st === 'active' && confirming !== s.id && (
                  <Button type="button" onClick={() => setConfirming(s.id)}>{t('revoke')}<span className="sr-only"> {who}</span></Button>
                )}
                {confirming === s.id && (
                  <div role="group" aria-label={t('revokeConfirm', { id: who })} className="grid gap-2">
                    <p>{t('revokeConfirm', { id: who })}</p>
                    <div className="flex gap-2">
                      <Button type="button" onClick={() => revoke.mutate(s.id)} disabled={revoke.isPending}>{t('revokeYes')}</Button>
                      <Button type="button" onClick={() => setConfirming(null)}>{t('cancel')}</Button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}

/** Repeated diagonal text; decorative (aria-hidden) and click-through. The visible banner carries the same info for AT. */
export function Watermark({ text }: { text: string }) {
  return (
    <div
      data-testid="watermark"
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 z-10 select-none overflow-hidden"
    >
      <div className="absolute -inset-1/2 grid -rotate-[30deg] grid-cols-3 content-around gap-x-8 gap-y-10 text-sm font-semibold opacity-25">
        {Array.from({ length: 60 }, (_, i) => <span key={i} className="whitespace-nowrap">{text}</span>)}
      </div>
    </div>
  );
}

export function SharedView({ shareId }: { shareId: string }) {
  const t = useTranslations('sharing');
  const r = useTranslations('viewer');
  const locale = useLocale();
  const me = useQuery({ queryKey: ['me'], queryFn: getMe });
  const q = useQuery({ queryKey: ['shared', shareId], queryFn: () => getSharedFindings(shareId) });
  const meta = useQuery({ queryKey: ['shared-meta', shareId], queryFn: () => getSharedShare(shareId) });
  if (q.isPending || me.isPending || meta.isPending) return <p role="status">{t('loading')}</p>;
  const err = q.error ?? meta.error;
  if (q.isError || meta.isError || !q.data || !meta.data) {
    const ended = err instanceof ApiError && (err.status === 403 || err.status === 404);
    return ended ? (
      <section aria-labelledby="ended"><h2 id="ended" className="text-lg font-semibold">{t('endedTitle')}</h2><p>{t('endedBody')}</p></section>
    ) : (
      <Alert tone="danger">{t('error')}</Alert>
    );
  }
  const until = new Date(meta.data.expires_at).toLocaleString(locale); // server-side expiry, not a URL hint
  const info = t('watermark', { id: me.data ? shortId(me.data.sub) : '?', share: shortId(shareId), until });
  const region = (c: string) => (r.has(`regions.${c}`) ? r(`regions.${c}`) : c);
  return (
    <div className="grid gap-4">
      <p role="status" className="rounded-md p-3 ring-1 ring-[var(--ml-color-brand-border)]">{t('banner', { info })}</p>
      <div className="relative">
        <BodyViewer regions={toRegions(q.data.findings)} model="body" />
        <Watermark text={info} />
      </div>
      <section aria-labelledby="shared-list" className="grid gap-2">
        <h2 id="shared-list" className="text-lg font-semibold">{t('findingsTitle')}</h2>
        <p className="text-sm text-[var(--ml-color-brand-textMuted)]">{t('readOnlyNote')}</p>
        {q.data.findings.length === 0 ? (
          <p>{t('noFindings')}</p>
        ) : (
          <ul className="list-disc pl-5">
            {q.data.findings.map((f, i) => <li key={i}>{f.label ?? region(f.region_code)}</li>)}
          </ul>
        )}
      </section>
    </div>
  );
}
