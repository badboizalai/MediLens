# Module Structure

```
apps/api/src/medilens/
├── core/            config.py, logging.py, security.py (JWT, current_user), db.py (async session), errors.py (Problem Details), telemetry.py
├── shared/          pagination.py, idempotency.py, outbox.py, audit.py, ids.py (uuid7), clock.py
└── modules/<name>/
    ├── api/         router.py, dto.py
    ├── application/ services.py (use cases), policies.py
    ├── domain/      models.py (entities/value objects), rules.py (BR-xxx), events.py, ports.py (repo/provider interfaces)
    └── infra/       repository.py (SQLAlchemy), tables.py, adapters/
```

Modules: identity, patient, document, extraction, anatomy, clinical, knowledge, sharing, notification, audit, admin.

## Dependency rules (enforced by import-linter)
- `api` may import `application`, `core`, `shared`.
- `application` may import `domain`, `shared`, `core` and other modules' **application** public functions only.
- `domain` imports nothing from `infra`, `api`, frameworks (pure Python + pydantic allowed for value objects).
- `infra` implements `domain.ports`.

## Naming
- Use case functions: verb + noun (`confirm_extraction`, `create_share`).
- Rules: `ensure_<condition>` raising domain errors mapped to Problem Details (`ensure_fields_confirmed` → BR-012).
- Events: past tense (`ExtractionConfirmed`).
- Tables: plural snake_case; columns snake_case; JSON camelCase via DTO aliases.

## import-linter contract example
```ini
[importlinter:contract:layers]
name = Layered modules
type = layers
layers =
    medilens.modules.*.api
    medilens.modules.*.application
    medilens.modules.*.domain
containers = medilens

[importlinter:contract:no-cross-infra]
name = No module imports another module's infra
type = forbidden
source_modules = medilens.modules
forbidden_modules = medilens.modules.*.infra
allow_indirect_imports = True
```
