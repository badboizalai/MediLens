# Error Catalog (Problem Details `type` suffixes under https://medilens.app/errors/)

| HTTP | type | When | Rule |
| --- | --- | --- | --- |
| 400 | validation | Request body/query fails schema | SEC-AP-01 |
| 401 | unauthenticated | Missing/expired token | SEC-ID-04 |
| 403 | consent-required | No current consent for the action | BR-002 |
| 403 | mfa-required | Role requires MFA | BR-003 |
| 404 | not-found | Missing **or** not owned/shared | BR-006 |
| 409 | duplicate-document | Same file or same visit/diagnosis | BR-016 |
| 409 | version-conflict | ETag mismatch | BE-API-09 |
| 409 | invalid-state | Action not allowed in current document state | state machine |
| 412 | precondition-failed | If-Match missing on PATCH | BE-API-09 |
| 413 | file-too-large | > 20 MB | BR-010 |
| 415 | unsupported-media | Not JPG/PNG/HEIC/PDF | BR-010 |
| 422 | low-quality-image | Blurry/low resolution | BR-011 |
| 422 | unconfirmed-fields | Confirm with pending low-confidence fields | BR-012 |
| 422 | share-expiry-invalid | Expiry > 90 days | BR-030 |
| 429 | rate-limited | Quota exceeded | SEC-AP-08 |
| 503 | ai-unavailable | Circuit breaker open | resilience |
| 500 | internal | Unexpected; message generic, details only in logs (no PHI) | SEC-AP-09 |

Domain exceptions map 1:1 to these in `core/errors.py`; never leak stack traces or SQL errors.
