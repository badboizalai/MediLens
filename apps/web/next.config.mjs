import createNextIntlPlugin from 'next-intl/plugin';

import { buildSecurityHeaders } from './next.config.headers.mjs';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

const securityHeaders = buildSecurityHeaders({
  prod: process.env.NODE_ENV === 'production',
  apiOrigin: process.env.NEXT_PUBLIC_API_BASE_URL,
  storageOrigin: process.env.NEXT_PUBLIC_STORAGE_ORIGIN,
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  output: 'standalone',
  // `*.svg?raw` imports the anatomy SVG as a string (parsed into React elements, never injected as HTML).
  webpack(config) {
    config.module.rules.push({ test: /\.svg$/, resourceQuery: /raw/, type: 'asset/source' });
    const asset = config.module.rules.find((r) => r.test?.test?.('.svg'));
    if (asset && asset.resourceQuery === undefined) asset.resourceQuery = { not: [/raw/] };
    return config;
  },
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
};

export default withNextIntl(nextConfig);
