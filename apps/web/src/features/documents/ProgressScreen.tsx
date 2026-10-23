'use client';

import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { useLocale, useTranslations } from 'next-intl';
import { useState } from 'react';
import { Alert, Button, Card } from '@/components/ui';
import { getDocument } from '@/lib/api/client';
import { isTerminal, viewOf, type View } from './progressView';

const POLL_MS = 2000;
const STEPS = ['queued', 'reading', 'extracting'] as const;

// No app-wide QueryClientProvider exists yet; the route owns one (same as review).
export function ProgressScreen(props: { documentId: string; pollMs?: number }) {
  const [client] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: false } } }));
  return (
    <QueryClientProvider client={client}>
      <Progress {...props} />
    </QueryClientProvider>
  );
}

function Progress({ documentId, pollMs = POLL_MS }: { documentId: string; pollMs?: number }) {
  const t = useTranslations('progress');
  const locale = useLocale();
  const doc = useQuery({
    queryKey: ['document-status', documentId],
    queryFn: () => getDocument(documentId),
    // Poll until a terminal status; transient errors keep polling. SSE replaces this in S6-T53d2.
    refetchInterval: (q) =>
      q.state.data && isTerminal(viewOf(q.state.data.status, q.state.data.retake_reason)) ? false : pollMs,
  });

  if (doc.isPending) return <p role="status">{t('loading')}</p>;
  const view: View = doc.data ? viewOf(doc.data.status, doc.data.retake_reason) : { kind: 'working', step: 0 };
  const upload = `/${locale}/upload`;
  const link = (href: string, label: string, primary = true) => (
    <Button asChild variant={primary ? 'primary' : 'secondary'}>
      <a href={href}>{label}</a>
    </Button>
  );

  switch (view.kind) {
    case 'ready':
      return (
        <Alert tone="success" title={t('ready.title')}>
          <p role="status">{t('ready.body')}</p>
          {link(`/${locale}/documents/${documentId}/review`, t('ready.action'))}
        </Alert>
      );
    case 'retake':
      return (
        <Alert tone="warning" title={t('retake.title')}>
          <p role="status">{t(`retake.reason.${view.reason ?? 'generic'}`)}</p>
          <p>{t('retake.note')}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {link(upload, t('retake.action'))}
            {link(`${upload}#capture-tips`, t('retake.guide'), false)}
          </div>
        </Alert>
      );
    case 'rejected':
      return (
        <Alert tone="danger" title={t('rejected.title')}>
          <p role="status">{t('rejected.why')}</p>
          <div className="mt-2">{link(upload, t('rejected.action'))}</div>
        </Alert>
      );
    case 'failed':
      return (
        <Alert tone="danger" title={t('failed.title')}>
          <p role="status">{t('failed.body')}</p>
          <div className="mt-2">{link(upload, t('failed.action'))}</div>
        </Alert>
      );
    case 'working':
      return (
        <Card>
          <p role="status">{t(`stage.${STEPS[view.step]}`)}</p>
          <ol aria-label={t('steps')} className="mt-3 grid gap-1">
            {STEPS.map((s, i) => (
              <li key={s} aria-current={i === view.step ? 'step' : undefined}>
                <span aria-hidden="true">{i < view.step ? '✓' : i === view.step ? '●' : '○'} </span>
                {t(`stage.${s}`)}
              </li>
            ))}
          </ol>
          <p className="mt-3">{t('leave')}</p>
        </Card>
      );
  }
}
