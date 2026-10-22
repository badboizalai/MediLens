# apps/phi-service
Isolated PHI store/service (level A) with key hierarchy (SEC-AR). Owner: medilens-security-engineer.

Stores direct identifiers (display name, birth date/year, phone, email) apart from clinical data and
issues an opaque `subject_key` (the Identity Link). Each field is AES-256-GCM encrypted under a
per-subject data key; the data key is wrapped by a KEK (envelope encryption). AAD binds ciphertext
to `subject_key` and field name.

| Endpoint | Purpose |
|---|---|
| `POST /v1/subjects` | create, returns `subject_key` |
| `GET /v1/subjects/{key}` | decrypt and return identifiers |
| `DELETE /v1/subjects/{key}` | crypto-shred: delete wrapped data key and ciphertext |

Config (env): `PHI_SERVICE_TOKEN` (shared bearer for service-to-service auth; **temporary**, to be
replaced by mTLS/IAM), `PHI_KEK_B64` (base64 32-byte local-dev KEK; cloud uses KMS via another
`Encryptor`). Unset token denies everything; unset KEK uses an ephemeral key.

Audit: one log line per access with `subject_key` and outcome only, never PHI values.
SQL repository is a stub: TODO S4-T34b. Tests: `uv run pytest apps/phi-service -q`.
