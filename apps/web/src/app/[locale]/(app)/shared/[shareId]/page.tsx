import { getTranslations } from 'next-intl/server';
import { SharingProviders } from '@/features/sharing/SharingScreens';

export default async function SharedPage({ params }: { params: Promise<{ shareId: string }> }) {
  const { shareId } = await params;
  const t = await getTranslations('sharing');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('sharedTitle')}</h1>
      <SharingProviders mode="shared" shareId={shareId} />
    </main>
  );
}
