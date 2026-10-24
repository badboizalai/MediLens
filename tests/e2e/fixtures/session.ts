import { createRequire } from 'node:module';
import path from 'node:path';
import type { BrowserContext } from '@playwright/test';

const SECRET = process.env.AUTH_SECRET ?? 'e2e-only-synthetic-secret-not-for-real-use';
const COOKIE = 'authjs.session-token'; // http (non-secure) cookie name; also the JWT salt

/** Sign in a synthetic user by minting the Auth.js session JWT the server's auth() accepts. */
export async function signInAs(context: BrowserContext, baseURL: string, sub = 'user-a') {
  // next-auth is only installed under apps/web (pnpm), so resolve it from there.
  const req = createRequire(path.resolve(__dirname, '../../../apps/web/package.json'));
  const { encode } = req('next-auth/jwt') as typeof import('next-auth/jwt');
  const token = await encode({
    token: { sub, name: 'Synthetic User', email: `${sub}@example.invalid` },
    secret: SECRET,
    salt: COOKIE,
  });
  await context.addCookies([{ name: COOKIE, value: token, url: baseURL, httpOnly: true, sameSite: 'Lax' }]);
}
