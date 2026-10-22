# Authentication and authorization (S3-T27)

## Flow
1. The browser talks only to the **web BFF** (Next.js server). The BFF runs OIDC authorization-code + PKCE against the IdP (Keycloak locally, AWS Cognito in cloud).
2. The BFF keeps tokens server-side and sets only a session cookie on the browser. Tokens never reach JS or `localStorage`.
3. The BFF calls the API with `Authorization: Bearer <access token>`.
4. The API **only validates** tokens (it never issues them): signature via the issuer JWKS, `iss`, `aud`, `exp`, then maps claims to a `Principal(sub, roles)`.

## BFF cookie guidance (web app)
| Attribute | Value | Why |
|---|---|---|
| `HttpOnly` | yes | Not readable by script (XSS) |
| `Secure` | yes (prod/staging; localhost exempt) | HTTPS only |
| `SameSite` | `Lax` | CSRF baseline; still allows the IdP redirect back |
| `Path` | `/` | |
| Lifetime | session cookie, server-side expiry <= refresh-token lifetime | |

State-changing BFF routes additionally check `Origin`/a CSRF token. Use the `__Host-` cookie prefix in prod.

## API configuration (`MEDILENS_OIDC_*`)
| Variable | Keycloak (local) | Cognito |
|---|---|---|
| `ISSUER` | `http://localhost:8080/realms/medilens` | `https://cognito-idp.<region>.amazonaws.com/<pool-id>` |
| `AUDIENCE` | `medilens-api` (audience mapper) | app client id |
| `JWKS_URL` | `<issuer>/protocol/openid-connect/certs` | `<issuer>/.well-known/jwks.json` |
| `ROLES_CLAIMS` | `realm_access.roles` | `cognito:groups` |

Note: Cognito access tokens carry `client_id` instead of `aud`; configure a resource server or validate ID tokens, otherwise the `aud` check will (correctly) reject.

## Behaviour
- Algorithms are pinned (default `RS256`); `none`/HS* and tokens without `kid` are rejected.
- JWKS is cached (TTL 1 h). An unknown `kid` triggers one refresh, rate limited to once per 30 s, so key rotation works without a restart and a flood of bad `kid`s cannot hammer the IdP.
- Library: **PyJWT[crypto]** chosen over python-jose: actively maintained, smaller surface, no known unpatched CVEs in the JWT path, and explicit algorithm allow-list.
- Errors are RFC 9457 Problem Details (`application/problem+json`): missing/invalid/expired token -> 401 `MEDILENS-401`; missing role -> 403 `MEDILENS-403`. Messages never reveal why a token failed.

## Usage
```python
from medilens.modules.identity.api.dependencies import get_current_user, require_role

@router.get("/x")
def x(user: Principal = Depends(get_current_user)): ...
@router.get("/admin", dependencies=[Depends(require_role("admin"))]): ...
```
Other modules must not import identity internals directly (import-linter); until a shared port exists, take the `Principal` via the dependency only.
Ownership checks (IDOR) remain each module's job; roles are not a substitute (SEC-AZ-01/02).
