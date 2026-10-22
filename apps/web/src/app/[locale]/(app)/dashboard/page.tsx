import { getTranslations } from 'next-intl/server';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');
  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <p className="mt-2 text-neutral-700">{t('empty')}</p>
    </main>
  );
}
