// Security headers, kept apart from next.config.mjs so tests can import them.
// shortcut: static CSP keeps 'unsafe-inline' for scripts (Next inline bootstrap); move to
// nonce + middleware when the app can accept fully dynamic rendering.

const origin = (url) => {
  try {
    return url ? new URL(url).origin : '';
  } catch {
    return '';
  }
};

/** @param {{ prod: boolean, apiOrigin?: string, storageOrigin?: string }} o */
export function buildCsp({ prod, apiOrigin, storageOrigin }) {
  return [
    "default-src 'self'",
    // 'unsafe-eval' is dev only (React refresh); production never gets it.
    `script-src 'self' 'unsafe-inline'${prod ? '' : " 'unsafe-eval'"}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:", // GLB textures / image previews
    "font-src 'self'",
    // API origin from env; storage origin for presigned PUTs; dev adds HMR websocket.
    ['connect-src', "'self'", origin(apiOrigin), origin(storageOrigin), prod ? '' : 'ws: http://localhost:*']
      .filter(Boolean)
      .join(' '),
    "worker-src 'self' blob:", // Draco/meshopt decoders
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    ...(prod ? ['upgrade-insecure-requests'] : []),
  ].join('; ');
}

export function buildSecurityHeaders(opts) {
  return [
    { key: 'Content-Security-Policy', value: buildCsp(opts) },
    { key: 'X-Frame-Options', value: 'DENY' },
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
    // Camera only for same-origin capture; everything else off.
    { key: 'Permissions-Policy', value: 'camera=(self), microphone=(), geolocation=(), payment=(), usb=()' },
    { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' },
  ];
}
