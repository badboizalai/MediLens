import NextAuth from 'next-auth';
import { buildAuthConfig } from './config';

/** Authorization code + PKCE; session is a JWT in an HttpOnly cookie (Auth.js default). */
export const { handlers, auth, signIn, signOut } = NextAuth(buildAuthConfig());
