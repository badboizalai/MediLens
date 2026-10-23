'use client';

import dynamic from 'next/dynamic';
import { useTranslations } from 'next-intl';

function Loading() {
  const t = useTranslations('viewer3d');
  return <p role="status" className="text-sm">{t('loading')}</p>;
}

/** Use this from pages: keeps three.js out of the initial bundle. */
export const BodyViewer3DLazy = dynamic(() => import('./BodyViewer3D').then((m) => m.BodyViewer3D), {
  ssr: false,
  loading: Loading,
});
