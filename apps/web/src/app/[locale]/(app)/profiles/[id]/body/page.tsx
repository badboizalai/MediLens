import { getTranslations } from 'next-intl/server';
import { TimelineProviders } from '@/features/timeline/TimelineScreen';

export default async function ProfileBodyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTranslations('timeline');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('bodyTitle')}</h1>
      <TimelineProviders profileId={id} view="body" />
    </main>
  );
}
