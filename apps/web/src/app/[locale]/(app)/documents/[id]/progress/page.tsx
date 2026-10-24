import { getTranslations } from 'next-intl/server';
import { ProgressScreen } from '@/features/documents/ProgressScreen';

export default async function ProgressPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTranslations('progress');
  return (
    <main className="mx-auto max-w-2xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('title')}</h1>
      <ProgressScreen documentId={id} />
    </main>
  );
}
