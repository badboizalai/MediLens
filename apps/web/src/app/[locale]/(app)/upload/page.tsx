import { getTranslations } from 'next-intl/server';
import { UploadScreen } from '@/features/documents/UploadScreen';

// "me" is resolved to the signed-in user's default profile by the API.
export default async function UploadPage() {
  const t = await getTranslations('upload');
  return (
    <main className="mx-auto max-w-5xl p-4 md:p-8">
      <h1 className="mb-4 text-2xl font-semibold">{t('title')}</h1>
      <UploadScreen profileId="me" />
    </main>
  );
}
