# apps/api — FastAPI modular monolith
Hexagonal modules under `src/medilens/modules/<name>/{api,application,domain,infra}`. Rules: `api → application → domain`; `infra` implements domain interfaces; modules never query each other's tables (enforced by `import-linter`, run `make api-lint`). Owner skill: `medilens-backend-engineer`.

## Extraction review (S7-T63)
- `GET /v1/documents/{id}/fields` - latest run fields; `needs_confirmation` = confidence < 0.7 (BR-012)
- `PATCH /v1/documents/{id}/fields/{field_id}` `{user_value}` - edit and confirm one field
- `POST /v1/documents/{id}/confirm` - 409 listing unconfirmed low-confidence field ids, else 204 + audit event

Other users' documents/fields return 404 (RLS + owner scope). Audit rows carry actor/action/ids only.
