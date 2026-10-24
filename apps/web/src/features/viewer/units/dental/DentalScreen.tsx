'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { Alert } from '@/components/ui';
import { newClient, useVisits } from '../../../timeline/api';
import { Odontogram } from './Odontogram';
import { toTeeth } from './toTeeth';

/** Page-level wrapper: loads the profile data and draws the tooth ones. */
export function DentalScreen({ profileId }: { profileId: string }) {
  const [client] = useState(newClient);
  return (
    <QueryClientProvider client={client}>
      <Dental profileId={profileId} />
    </QueryClientProvider>
  );
}

function Dental({ profileId }: { profileId: string }) {
  const t = useTranslations('viewerUi.dental');
  const q = useVisits(profileId);
  if (q.isPending) return <p role="status">{t('loading')}</p>;
  if (q.isError) return <Alert tone="danger">{t('error')}</Alert>;
  return <Odontogram teeth={toTeeth(q.data.flatMap((v) => v.findings))} />;
}
