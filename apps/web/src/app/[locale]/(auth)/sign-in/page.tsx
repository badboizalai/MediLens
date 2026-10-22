import { getLocale, getTranslations } from 'next-intl/server';
import { signIn } from '@/lib/auth';

export default async function SignInPage() {
  const t = await getTranslations('signIn');
  const locale = await getLocale();
  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <p className="mt-2 text-neutral-700">{t('description')}</p>
      <form
        className="mt-6"
        action={async () => {
          'use server';
          await signIn('oidc', { redirectTo: `/${locale}/dashboard` });
        }}
      >
        <button
          type="submit"
          className="rounded-md bg-neutral-900 px-4 py-2 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        >
          {t('submit')}
        </button>
      </form>
    </main>
  );
}
