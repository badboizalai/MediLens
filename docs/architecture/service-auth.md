# Service authentication (internal services)

Status: interim (S5-F15). Applies to `apps/ai-gateway` (`POST /v1/complete`) and `apps/phi-service` (`/v1/subjects*`). `/healthz` is open.

## Scheme: short-lived HMAC service token

`Authorization: Bearer <b64url(claims)>.<b64url(HMAC-SHA256(secret, b64url(claims)))>`

| Claim | Meaning |
| --- | --- |
| `iss` | caller id (e.g. `api`, `worker`) |
| `aud` | target service: `ai-gateway` or `phi-service`; a token for one is rejected by the other |
| `iat` / `exp` | `exp - iat <= 300 s`; `iat` may be at most 30 s in the future |
| `nonce` | random, single use: a verifier rejects a replayed nonce until `exp` |
| `tenants`, `profiles` | (ai-gateway) allowed scope lists |

Rules:
- Secret per target service from settings: `AI_GATEWAY_SERVICE_SECRET`, `PHI_SERVICE_SECRET` (Secrets Manager in AWS). Different secrets per service. Unset/empty => every protected call is 401 (fail closed).
- Missing, malformed, tampered, expired, wrong-audience or replayed token => 401.
- AI Gateway: the request `tenant_id` and `profile_id` must be listed in the token's `tenants` / `profiles`; otherwise 403. No claim means no access. Callers cannot widen scope in the body.
- PHI service: startup refuses to run with an ephemeral random KEK unless `ENV=local`; set `PHI_KEK_B64` (32 bytes, base64) otherwise. Unset `ENV` counts as non-local.
- Callers mint a fresh token per request (`service_token.mint`). The helper (`service_token.py`) is deliberately duplicated in each app (no cross-app imports); keep the copies identical.
- Replay cache is per process in memory. With several replicas a token could be replayed once per replica within its <= 5 min life; acceptable interim, closed by the migration below.
- Never log tokens or secrets.

## Migration path to AWS IAM / mTLS

1. Put both services behind internal ALB/Service Connect in private subnets; security groups allow only known callers.
2. Replace the shared secret with SigV4 (IAM) on API Gateway/Lambda-style front or ALB OIDC with per-task IAM roles; `iss` becomes the task role ARN, `tenants`/`profiles` move to an authorization lookup on the caller identity.
3. Or mTLS via ACM Private CA (Service Connect TLS): the peer certificate subject replaces `iss`/`aud`.
4. Run both schemes in parallel behind a flag, switch callers, then delete the token verifier and the secrets.
