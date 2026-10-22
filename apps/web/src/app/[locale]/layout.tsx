import type { ReactNode } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { WebMcpProvider } from '@/lib/webmcp/WebMcpProvider';
import { ThemeStyle } from '@/components/ui';
import { Header } from './_header';
import '@/styles/globals.css';

export default async function RootLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages();
  return (
    <html lang={locale}>
      <head>
        <ThemeStyle />
      </head>
      <body>
        <NextIntlClientProvider messages={messages}>
          <WebMcpProvider />
          <Header />
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
