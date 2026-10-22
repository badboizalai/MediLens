import { getLocale, getTranslations } from 'next-intl/server';
import { auth, signIn, signOut } from '@/lib/auth';
import { LocaleSwitch } from './_locale-switch';

export async function Header() {
  const t = await getTranslations('nav');
  const locale = await getLocale();
  const session = await auth();
  const btn = 'ml-btn ml-btn--secondary';
  return (
    <header className="flex items-center justify-between border-b border-brand-border px-6 py-3">
      <a href={`/${locale}`} className="text-lg font-semibold">
        MediLens
      </a>
      <nav aria-label={t('label')} className="flex items-center gap-3">
        <LocaleSwitch label={t('language')} />
        {session ? (
          <form
            action={async () => {
              'use server';
              await signOut({ redirectTo: `/${locale}` });
            }}
          >
            <button type="submit" className={btn}>
              {t('signOut')}
            </button>
          </form>
        ) : (
          <form
            action={async () => {
              'use server';
              await signIn('oidc', { redirectTo: `/${locale}/dashboard` });
            }}
          >
            <button type="submit" className={btn}>
              {t('signIn')}
            </button>
          </form>
        )}
      </nav>
    </header>
  );
}
