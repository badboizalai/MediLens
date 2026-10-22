import type { NextAuthConfig } from 'next-auth';

/** Generic OIDC provider built from env (Keycloak locally, Cognito later). */
export function buildAuthConfig(env: NodeJS.ProcessEnv = process.env): NextAuthConfig {
  return {
    providers: [
      {
        id: 'oidc',
        name: 'MediLens',
        type: 'oidc',
        issuer: env.AUTH_OIDC_ISSUER,
        clientId: env.AUTH_OIDC_CLIENT_ID,
        clientSecret: env.AUTH_OIDC_CLIENT_SECRET,
        checks: ['pkce', 'state'],
        authorization: { params: { scope: 'openid profile email' } },
      },
    ],
    session: { strategy: 'jwt', maxAge: 60 * 30 },
    pages: { signIn: '/sign-in' },
    trustHost: true,
  };
}
