# apps/web
Next.js 15 App Router (VI/EN). Viewer uses plugins in `src/features/viewer/units/*` registered in `registry.ts`. Owner skills: `medilens-frontend-engineer`, `medilens-ux-ui-designer`.

## Environment (`.env.local`, never committed)
| Variable | Example (local) | Purpose |
| --- | --- | --- |
| `AUTH_SECRET` | `openssl rand -base64 32` | Auth.js session encryption |
| `AUTH_URL` | `http://localhost:3000` | Public URL of the web app |
| `AUTH_OIDC_ISSUER` | `http://localhost:8080/realms/medilens` | OIDC issuer (Keycloak locally, Cognito later) |
| `AUTH_OIDC_CLIENT_ID` | `medilens-web` | OIDC client id |
| `AUTH_OIDC_CLIENT_SECRET` | — | OIDC client secret |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | API base URL |
| `NEXT_PUBLIC_STORAGE_ORIGIN` | `http://localhost:4566` | Presigned-upload origin, allowed in CSP `connect-src` |
| `NEXT_PUBLIC_DEV_PROFILE_ID` | a synthetic UUID | Local dev only, until the profile picker exists |
