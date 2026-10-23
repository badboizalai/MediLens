import { getTranslations } from 'next-intl/server';
import { ReviewProviders } from '@/features/review/ReviewProviders';

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTranslations('review');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('title')}</h1>
      <ReviewProviders documentId={id} />
    </main>
  );
}
