import { describe, expect, it } from 'vitest';
// @ts-ignore -- plain .mjs shared with next.config.mjs
import { buildCsp, buildSecurityHeaders } from '../../next.config.headers.mjs';

const prod = { prod: true, apiOrigin: 'https://api.medilens.test/v1', storageOrigin: 'https://s3.test' };
const dir = (csp: string, name: string) => csp.split('; ').find((d) => d.startsWith(name)) ?? '';

describe('CSP', () => {
  const csp: string = buildCsp(prod);

  it('is locked down in production', () => {
    expect(dir(csp, 'default-src')).toBe("default-src 'self'");
    expect(dir(csp, 'script-src')).not.toContain('unsafe-eval');
    expect(dir(csp, 'object-src')).toBe("object-src 'none'");
    expect(dir(csp, 'frame-ancestors')).toBe("frame-ancestors 'none'");
    expect(dir(csp, 'base-uri')).toBe("base-uri 'self'");
  });

  it('connect-src is self + API origin + storage origin only', () => {
    expect(dir(csp, 'connect-src')).toBe("connect-src 'self' https://api.medilens.test https://s3.test");
  });

  it('keeps the 3D viewer working (blob workers, data/blob textures)', () => {
    expect(dir(csp, 'worker-src')).toContain('blob:');
    expect(dir(csp, 'img-src')).toContain('blob:');
  });

  it('dev relaxes eval and HMR only', () => {
    const dev: string = buildCsp({ prod: false });
    expect(dir(dev, 'script-src')).toContain("'unsafe-eval'");
    expect(dir(dev, 'connect-src')).toContain('ws:');
  });

  it('ignores a malformed API origin', () => {
    expect(dir(buildCsp({ prod: true, apiOrigin: 'not a url' }), 'connect-src')).toBe("connect-src 'self'");
  });
});

describe('response headers', () => {
  const h = Object.fromEntries(
    (buildSecurityHeaders(prod) as { key: string; value: string }[]).map((x) => [x.key, x.value]),
  );

  it('sets the required set', () => {
    expect(h['X-Content-Type-Options']).toBe('nosniff');
    expect(h['Referrer-Policy']).toBe('strict-origin-when-cross-origin');
    expect(h['Strict-Transport-Security']).toContain('max-age=');
    expect(h['Cross-Origin-Opener-Policy']).toBe('same-origin');
    expect(h['Permissions-Policy']).toContain('camera=(self)');
    expect(h['Permissions-Policy']).toContain('microphone=()');
  });
});
