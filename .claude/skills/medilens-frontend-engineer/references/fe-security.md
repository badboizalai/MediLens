# Frontend Security

| Code | Requirement | How |
| --- | --- | --- |
| FE-SEC-01 | Tokens only in HttpOnly, Secure, SameSite cookies managed server-side | Route handlers; no tokens in JS memory/localStorage |
| FE-SEC-02 | CSP with nonce; no inline scripts; `frame-ancestors 'none'` | Next.js middleware sets per-request nonce |
| FE-SEC-03 | Never render HTML from LLM/user content | react-markdown with `skipHtml`, links `rel="noopener noreferrer"`; DOMPurify if HTML unavoidable |
| FE-SEC-04 | No PHI in URLs, analytics, RUM, error tracking | IDs only in routes; Sentry `beforeSend` scrubber; RUM page names templated |
| FE-SEC-05 | Supply chain: lockfile, audit, pinned versions, scripts only from own origin | npm audit/Dependabot, SRI not needed for self-hosted |
| FE-SEC-06 | Clear state on logout | `queryClient.clear()`, reset Zustand stores, revoke object URLs |
| FE-SEC-07 | Download/preview of originals via short-lived presigned URLs; revoke blob URLs | — |
| FE-SEC-08 | CSRF token for state-changing BFF routes | double-submit or header token |

Example CSP:
```
default-src 'self'; script-src 'self' 'nonce-{n}' 'strict-dynamic'; style-src 'self' 'unsafe-inline';
img-src 'self' blob: data: https://assets.medilens.app; connect-src 'self' https://api.medilens.app;
worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; object-src 'none'
```
