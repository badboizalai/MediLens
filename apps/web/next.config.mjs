import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

// Baseline CSP. 'unsafe-inline' is required by Next.js inline bootstrap scripts
// until nonce-based CSP is added; 'unsafe-eval' is dev-only (React refresh).
const csp = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === 'production' ? '' : " 'unsafe-eval'"}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  // Presigned PUTs go straight to object storage; its origin comes from the environment.
  `connect-src 'self'${process.env.NEXT_PUBLIC_STORAGE_ORIGIN ? ` ${process.env.NEXT_PUBLIC_STORAGE_ORIGIN}` : ''}`,
  "worker-src 'self' blob:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join('; ');

const securityHeaders = [
  { key: 'Content-Security-Policy', value: csp },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
];

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
