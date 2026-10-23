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

## Cascade v1 (S7-T65)
Request `tier: "auto"` (absent = v0 single call) and optional opaque `document_id`: cache hit returns; else Tier S; if confidence < `escalation_threshold` (default 0.7 = BR-012 review threshold) or the provider flags a schema-invalid output, exactly one escalation to Tier M, never beyond (response has `escalated`, `needs_review`, `tier`, `confidence`; `cost_usd`/tokens are summed over both calls). Tier L / human review are out of scope.

- Config (`config/gateway.toml`, env overrides `AI_GATEWAY_TIER_S_MODEL`, `AI_GATEWAY_TIER_M_MODEL`, `AI_GATEWAY_ESCALATION_THRESHOLD`): tier models must be in the allowlist; prices are now **USD per 1K tokens** (`prices_usd_per_1k`), still assumptions.
- Providers report `ProviderResult.confidence` (None = unreported, never escalates) and `schema_valid`.
- Metering: `Gateway.document_usage(document_id)` returns USD, tokens and per-tier call counts (in memory, cache hits not counted). Logs carry ids/numbers plus the already-redacted text as in v0.

Test: `uv run pytest apps/ai-gateway -q`

## Safety guardrails (S10-T96)
`CompletionRequest(traffic="qa", locale="vi"|"en")` turns on deterministic guardrails (`guardrails.py`) for explanation/Q&A traffic; extraction traffic (`traffic=None`) is untouched. Rules run on lowercased, diacritic-stripped text (VI with/without diacritics, EN).

- Input check before redaction and any provider call: `emergency` (chest pain, breathing trouble, ... BR-023/BR-041) returns fixed copy that leads with 115; `dosing`, `med_change`, `prognosis`, `diagnosis` return a fixed refusal pointing to the treating clinician (BR-023/BR-042). No provider call in either case.
- Output check on the provider answer: dose patterns (`500 mg`, `2 viên`, `3 lần/ngày`; lab units like `mg/dL` are allowed), survival-time phrases and "you have <disease>" are replaced by the refusal.
- Response carries `guardrail: {category, action}` (`emergency|blocked_input|blocked_output`); logs hold category/action only, never prompt text.
- Starter set: `tests/data/guardrail-cases.v1.jsonl` (synthetic, 83 cases incl. benign controls). Gate: >= 95% overall, 100% emergency, 0 benign false-blocks. Full red-team set is S10-T98.
- Limits: regex rules, not a classifier; paraphrases will slip through. HTTP `CompleteBody` exposes `traffic` (`"qa"`) and `locale` (`vi`|`en`).

## Semantic cache and token quota (S10-T97)
- **QA cache** (`cache.py`): only `traffic="qa"` answers that passed guardrails. Key = (tenant, profile, locale, prompt_version) + normalised **redacted** question (lowercase, no diacritics/punctuation, token-set Jaccard >= 0.85). Per-profile scope, so no cross-user hits. TTL = `cache_ttl_s`, max 1000 entries, in-memory; `hits`/`misses` counters on `Gateway.qa_cache`. Guardrail refusals/emergency and extraction traffic are never cached. Shortcut: Jaccard, not embeddings; upgrade to pgvector/Redis later. The exact-match cache key now also includes `locale`.
- **Quota** (`quota.py`, SEC-AI-07): per (tenant, profile) daily input+output token budget (`daily_token_quota`, default 50000 = assumption, env `AI_GATEWAY_DAILY_TOKEN_QUOTA`, UTC day). Checked before the provider call (the last call may overshoot); cache hits are free. Over quota -> HTTP 429 `quota_exceeded` with `Retry-After` (seconds to next UTC day).
- HTTP response carries `guardrail` and `cached`.
