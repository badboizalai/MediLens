import { getTranslations } from 'next-intl/server';
import { DentalScreen } from '@/features/viewer/units/dental/DentalScreen';

export default async function ProfileDentalPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTranslations('viewerUi.dental');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('title')}</h1>
      <DentalScreen profileId={id} />
    </main>
  );
}
