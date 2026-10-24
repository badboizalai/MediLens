import { getTranslations } from 'next-intl/server';
import { SharingProviders } from '@/features/sharing/SharingScreens';

export default async function SharedPage({
  params,
  searchParams,
}: {
  params: Promise<{ shareId: string }>;
  searchParams: Promise<{ exp?: string }>;
}) {
  const { shareId } = await params;
  const { exp } = await searchParams; // display-only hint for the watermark; access is enforced by the API
  const t = await getTranslations('sharing');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('sharedTitle')}</h1>
      <SharingProviders mode="shared" shareId={shareId} expiresAt={exp} />
    </main>
  );
}
