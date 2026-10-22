# Backend Testing Guide

| Layer | Scope | Tools | Target |
| --- | --- | --- | --- |
| Unit | domain rules, mappers, parsers | pytest, hypothesis | domain ≥ 90% coverage |
| Integration | repositories, RLS, outbox, presign | pytest + Testcontainers (postgres:16 with pgvector), LocalStack (S3, SQS) | main flows 100% |
| Contract | OpenAPI conformance | schemathesis (`st.from_asgi`) | 0 violations |
| Authorization | role × endpoint × ownership | generated parametrised tests | 100% operations |
| Worker | each job + chain with fake providers | pytest, moto/LocalStack | success, retry, DLQ, idempotency |
| Migration | upgrade/downgrade with data | Alembic + Testcontainers | pass |
| Performance | read/write endpoints | k6 against staging | NFR-02/03 |

## Fixtures
- `db` (transaction per test, rolled back), `client` (httpx AsyncClient with app), `user_factory`, `profile_factory`, `document_factory` with **synthetic** data only.
- `fake_llm`, `fake_ocr` providers returning recorded outputs.
- Freeze time with `time-machine` for expiry tests.

## Naming
`test_br012_confirm_rejected_when_low_confidence_unconfirmed`, `test_sec_az_02_stranger_gets_404_on_document`.

## CI
`pytest -q --cov=medilens --cov-fail-under=80`, `schemathesis run`, `lint-imports`, `mypy --strict src/medilens/modules/*/domain`.
