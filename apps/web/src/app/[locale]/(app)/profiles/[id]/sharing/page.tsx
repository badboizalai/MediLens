import { getTranslations } from 'next-intl/server';
import { SharingProviders } from '@/features/sharing/SharingScreens';

export default async function ProfileSharingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTranslations('sharing');
  return (
    <main className="mx-auto max-w-3xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('title')}</h1>
      <SharingProviders mode="owner" profileId={id} />
    </main>
  );
}
