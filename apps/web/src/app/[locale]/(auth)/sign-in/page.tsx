import { getLocale, getTranslations } from 'next-intl/server';
import { Button } from '@/components/ui';
import { signIn } from '@/lib/auth';

export default async function SignInPage() {
  const t = await getTranslations('signIn');
  const locale = await getLocale();
  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <p className="mt-2 text-brand-text-muted">{t('description')}</p>
      <form
        className="mt-6"
        action={async () => {
          'use server';
          await signIn('oidc', { redirectTo: `/${locale}/dashboard` });
        }}
      >
        <Button type="submit">{t('submit')}</Button>
      </form>
    </main>
  );
}
