# API Standards

| Code | Standard |
| --- | --- |
| BE-API-01 | OpenAPI 3.1 is the source of truth; TS client generated; PRs include OpenAPI diff (oasdiff breaking check in CI) |
| BE-API-02 | Plural kebab-case nouns: `/api/v1/medical-documents/{documentId}/pages` |
| BE-API-03 | URL versioning; breaking → `/v2`; keep v1 ≥ 90 days with `Deprecation` and `Sunset` headers |
| BE-API-04 | JSON camelCase; DB snake_case; ISO-8601 UTC timestamps; dates `YYYY-MM-DD` |
| BE-API-05 | Cursor pagination `?limit=&cursor=`, max 100, response `{items, nextCursor}` |
| BE-API-06 | Filter/sort allowlist: `?status=confirmed&sort=-observedAt` |
| BE-API-07 | Errors RFC 9457 Problem Details with `traceId`, `errors[]` |
| BE-API-08 | `Idempotency-Key` required on important POSTs; store key+hash+response 24 h |
| BE-API-09 | `ETag` + `If-Match` on PATCH of extraction/condition → 412/409 on mismatch |
| BE-API-10 | Long tasks: `202 Accepted` + `Location` |
| BE-API-11 | Rate-limit headers `RateLimit-Limit`, `RateLimit-Remaining`, `Retry-After` |
| BE-API-12 | SSE for status and explanation streaming; heartbeat 15 s; cancellable |

## Core endpoints (v1)
| Method | Path | Purpose | Notes |
| --- | --- | --- | --- |
| GET | /me | current user + consents | |
| POST | /consents | give consent (type, termsVersion) | BR-002 |
| GET/POST | /patient-profiles | list/create profiles | caregiver profiles |
| POST | /medical-documents | create document + presigned upload URLs | Idempotency-Key |
| POST | /medical-documents/{id}/complete | mark uploaded → enqueue | 202 |
| GET | /medical-documents/{id} | status, pages | |
| GET | /medical-documents/{id}/events | SSE status | |
| GET | /extractions/{id} | fields with confidence + sources | ETag |
| PATCH | /extractions/{id}/fields/{fieldId} | correct a field | If-Match |
| POST | /extractions/{id}/confirm | confirm all | BR-012/013 |
| GET | /findings?unit=&from=&to= | confirmed findings for viewer | |
| GET | /observations?code=&from=&to= | lab series | |
| GET | /timeline | encounters with findings | BR-025 |
| GET | /units, /units/{code}/config | Unit catalog/config | cacheable, no PHI |
| POST | /explanations | ask question → SSE answer | guardrails |
| GET/POST/DELETE | /shares | share management | BR-030/031 |
| POST | /data-requests | export / delete / withdraw consent | BR-032, DSR |
| GET | /admin/audit-events | audit search (no PHI content) | admin + MFA |

## Example Problem Details
```json
{
  "type": "https://medilens.app/errors/unconfirmed-fields",
  "title": "Some fields still need your confirmation",
  "status": 422,
  "detail": "3 low-confidence fields must be confirmed before saving.",
  "instance": "/api/v1/extractions/0190.../confirm",
  "traceId": "1-6655c2a1-...",
  "errors": [{"field": "teeth[0].fdi", "code": "low_confidence"}]
}
```
