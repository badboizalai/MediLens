import NextAuth from 'next-auth';

/**
 * Generic OIDC provider configured by env (Keycloak locally, Cognito later).
 * Authorization code + PKCE; session is a JWT in an HttpOnly cookie (Auth.js default).
 */
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    {
      id: 'oidc',
      name: 'MediLens',
      type: 'oidc',
      issuer: process.env.AUTH_OIDC_ISSUER,
      clientId: process.env.AUTH_OIDC_CLIENT_ID,
      clientSecret: process.env.AUTH_OIDC_CLIENT_SECRET,
      checks: ['pkce', 'state'],
      authorization: { params: { scope: 'openid profile email' } },
    },
  ],
  session: { strategy: 'jwt', maxAge: 60 * 30 },
  pages: { signIn: '/sign-in' },
  trustHost: true,
});
