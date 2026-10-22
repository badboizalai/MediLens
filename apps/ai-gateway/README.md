# apps/ai-gateway
All LLM/OCR provider calls: redaction, cascade routing, cost/token accounting. Owner: medilens-mlops-engineer.

## v0 (S5-T44)
Python library (`medilens_ai_gateway.Gateway`) plus a thin FastAPI service (`POST /v1/complete`).

Pipeline: scope check -> model allowlist -> PII redaction (VI + EN) -> scoped cache -> provider call with timeout -> token/cost metering -> redacted logging.

- **Fail closed (O-03):** any redaction error (request or response) blocks the call; the provider is never reached.
- **Allowlist:** model ids live in `config/gateway.toml` (default `claude-haiku-5-5`, `claude-sonnet-5-5`); anything else is rejected with 403.
- **Cache (O-02):** SHA-256 of tenant + profile + prompt version + model + redacted prompt.
- **Metering:** prices in `config/gateway.toml` are **assumptions** to verify before quoting cost.
- **Logs:** only redacted prompt/response are logged. Redaction is a rule-based first layer (target recall >= 99% still to be measured on a labelled synthetic set).
- **Providers:** `Provider` protocol + deterministic `StubProvider` (used in tests, no network). Anthropic/Bedrock adapters, routing/cascade and quotas are out of scope for v0.

Test: `uv run pytest apps/ai-gateway -q`
