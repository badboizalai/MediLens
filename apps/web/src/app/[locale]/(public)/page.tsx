import { useTranslations } from 'next-intl';

export default function Home() {
  const t = useTranslations('home');
  return (
    <main className="p-8">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <p>{t('disclaimer')}</p>
    </main>
  );
}
