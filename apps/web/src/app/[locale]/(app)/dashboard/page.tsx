import { getLocale, getTranslations } from 'next-intl/server';
import { Button } from '@/components/ui';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');
  const locale = await getLocale();
  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <p className="mt-2 mb-4 text-brand-text-muted">{t('empty')}</p>
      <Button asChild>
        <a href={`/${locale}/upload`}>{t('upload')}</a>
      </Button>
    </main>
  );
}
