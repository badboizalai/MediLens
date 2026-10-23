# Security review: CSP, security headers, CORS (S9-T89)

Date 2026-10-24. Reviewer: security-engineer. Refs: OWASP ASVS L2 V14.4/V14.5, SEC-AP (web/API hardening), SEC-DP (no PHI caching). Method: code read plus automated header/CORS tests (below). No external scanner was run; no external scan results are claimed.

## Scope

| Surface | Browser-reachable | Action |
|---|---|---|
| `apps/web` (Next.js) | yes | headers hardened (`next.config.headers.mjs`) |
| `apps/api` (FastAPI) | yes (CORS from web origin) | CORS allow-list tightened, security-headers middleware |
| `apps/ai-gateway`, `apps/phi-service` | **no**: internal only, service-token auth (`docs/architecture/service-auth.md`), no CORS configured | left unchanged |

## Findings

| ID | Sev | Finding | SEC / ASVS | Status |
|---|---|---|---|---|
| H1 | Med | API sent no security headers (nosniff, framing, HSTS) and no `Cache-Control`; PHI JSON could be cached by shared caches/browsers | V14.4, SEC-DP | Fixed: `SecurityHeadersMiddleware` (nosniff, `X-Frame-Options: DENY`, CSP `default-src 'none'; frame-ancestors 'none'`, HSTS, `Cache-Control: no-store` unless a handler set its own) |
| H2 | Med | Wildcard CORS origin was rejected only in staging/prod; local/dev could ship `*` | V14.5.3 | Fixed: rejected in every env |
| H3 | Low | Web `connect-src` allowed storage origin but not the API origin (relied on same-origin proxy) | V14.4 | Fixed: API origin from `NEXT_PUBLIC_API_BASE_URL` |
| H4 | Low | Web missing COOP; `Permissions-Policy` set `camera=()` (blocks capture) | V14.4 | Fixed: COOP `same-origin`, `camera=(self)`, `payment/usb` off |
| H5 | Low | No `upgrade-insecure-requests` in prod | V14.4 | Fixed (prod only) |
| H6 | Med | `script-src 'unsafe-inline'` remains (Next inline bootstrap) | V14.4.3 | **Open** (residual, below) |

CORS (already correct, now tested): explicit origin list from typed `Settings.cors_origins`; explicit method and header allow-lists; credentials not enabled (Bearer tokens, no cookies on the API), so `Access-Control-Allow-Credentials` is never sent.

## Web CSP (production)

`default-src 'self'`; `script-src 'self' 'unsafe-inline'` (no `unsafe-eval`); `connect-src 'self' <API origin> <storage origin>`; `img-src 'self' data: blob:`; `worker-src 'self' blob:` (3D viewer / Draco decoders); `object-src 'none'`; `base-uri 'self'`; `form-action 'self'`; `frame-ancestors 'none'`; `upgrade-insecure-requests`. WebMCP (`navigator.modelContext`) is in-page JS and needs no CSP allowance. next-intl/next-auth use same-origin requests.
Dev relaxation (documented, never in production): `'unsafe-eval'` for React refresh, `ws:` and `http://localhost:*` in `connect-src` for HMR.

## Residual risks

- H6: nonce-based CSP needs dynamic rendering of every page (middleware nonce). Deferred; XSS exposure is reduced by React escaping, no `dangerouslySetInnerHTML` of user data (SVG is parsed to elements), and `object-src`/`base-uri` locks. Revisit before real-data gate G3-P.
- HSTS has no `preload`; submit only after the prod domain is fixed.
- CDN (CloudFront) response-headers policy and S3 bucket CORS live in Terraform and are outside this task's paths: confirm they mirror these headers and allow only the app origin.
- Static `X-Frame-Options` duplicates `frame-ancestors` for old browsers (intentional).

## How to run the checks

Automated: `cd apps/api && uv run pytest tests/test_security_headers.py -q` (preflight allowed vs disallowed origin, no wildcard in any env, headers on 200/404/preflight) and `pnpm --filter @medilens/web test` (`src/__tests__/security-headers.test.ts`, CSP directives prod vs dev).

Manual against a running stack:

```
curl -sI http://localhost:8000/healthz | grep -iE 'x-content-type|x-frame|content-security|cache-control|strict-transport'
curl -sI -X OPTIONS http://localhost:8000/v1/documents -H 'Origin: https://evil.example' -H 'Access-Control-Request-Method: POST'   # no Access-Control-Allow-Origin
curl -sI http://localhost:3000/ | grep -iE 'content-security|strict-transport|permissions|cross-origin-opener|referrer'
```
