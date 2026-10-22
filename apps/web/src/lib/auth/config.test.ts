import { describe, expect, it } from 'vitest';
import { buildAuthConfig } from './config';

describe('buildAuthConfig', () => {
  it('builds an OIDC provider with PKCE from env', () => {
    const cfg = buildAuthConfig({
      AUTH_OIDC_ISSUER: 'https://idp.example/realms/x',
      AUTH_OIDC_CLIENT_ID: 'cid',
      AUTH_OIDC_CLIENT_SECRET: 'secret',
    } as unknown as NodeJS.ProcessEnv);
    const p = cfg.providers[0] as unknown as Record<string, unknown>;
    expect(p.type).toBe('oidc');
    expect(p.issuer).toBe('https://idp.example/realms/x');
    expect(p.clientId).toBe('cid');
    expect(p.clientSecret).toBe('secret');
    expect(p.checks).toEqual(['pkce', 'state']);
  });

  it('uses a JWT session (cookie) and custom sign-in page', () => {
    const cfg = buildAuthConfig({} as NodeJS.ProcessEnv);
    expect(cfg.session?.strategy).toBe('jwt');
    expect(cfg.pages?.signIn).toBe('/sign-in');
  });
});
