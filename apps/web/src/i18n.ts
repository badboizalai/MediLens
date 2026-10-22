import { getRequestConfig } from 'next-intl/server';

export const locales = ['vi', 'en'] as const;
export const defaultLocale = 'vi';

export default getRequestConfig(async ({ requestLocale }) => {
  const locale = (await requestLocale) ?? defaultLocale;
  return { locale, messages: (await import(`../messages/${locale}.json`)).default };
});
