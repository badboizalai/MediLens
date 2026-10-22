# AI Gateway specification

## Responsibilities
Single egress for LLM/embedding calls · PII redaction · quotas and budgets · caching · routing (cascade) · model allowlist · schema validation · metering · redacted logging · circuit breaking and fallback.

## Request contract (internal)
```json
{"task": "extract|classify|map|ner|explain|judge", "unit": "cardio", "prompt_version": "extract-v2",
 "schema_version": "cardio-1.3", "input": {"text": "...", "images": []}, "subject_key": "sk_…",
 "priority": "interactive|batch", "max_output_tokens": 800}
```
Response: `{"output": {...}, "tier": "M", "model_id": "...", "cache": "hit|miss", "tokens": {"in": 0, "cached": 0, "out": 0}, "usd": 0.0, "latency_ms": 0, "escalated": false}`.

## Flow
1. Caller auth (service IAM role / mTLS inside VPC); reject unknown callers.
2. Redact PII (names, phones, IDs, addresses, emails) — recall ≥ 99% on the test set; keep a reversible map only inside the PHI Service when needed for display.
3. Quota: per `subject_key` per day (documents, questions, tokens); global daily budget; reject with 429 + friendly message.
4. Cache: exact key `sha256(normalised input) + prompt_version + schema_version + model_id`; TTL per task; explanations may use a semantic cache keyed by article + normalised question.
5. Route per `router-config` (tier per task, escalation rules).
6. Call provider (Bedrock via VPC endpoint by default); timeout per tier; retries with jitter on throttling only.
7. Validate output against JSON Schema; on failure retry once with a repair prompt, then escalate one tier, then return `needs_review`.
8. Meter and log (redacted), emit metrics.

## Configuration
Stored in AppConfig with validation: allowlist of model ids per environment, tier mapping per task, thresholds, budgets, quotas, cache TTLs, fallback provider order, kill switches per task.

## Errors
`budget_exceeded`, `quota_exceeded`, `provider_unavailable` (after fallback), `schema_invalid`, `blocked_by_guardrail`, `input_too_large`. All map to Problem Details in the API.

## Security
No internet egress except provider endpoints via VPC endpoints/allowlist; secrets in Secrets Manager; prompts versioned in Git and reviewed; logs retain 30 days, restricted (SEC-AI-08).
