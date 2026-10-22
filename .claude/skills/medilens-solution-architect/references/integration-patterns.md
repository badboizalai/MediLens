# Integration & Resilience Patterns (MediLens)

## 1. Async request–reply
Upload complete → `202 Accepted` + `Location: /api/v1/medical-documents/{id}` → FE subscribes to SSE `/api/v1/medical-documents/{id}/events`. Never hold an HTTP request during OCR/LLM.

## 2. Transactional outbox
```
BEGIN;
  INSERT INTO extraction_fields ...;
  UPDATE medical_documents SET status='confirmed' ...;
  INSERT INTO outbox(id, event_type, payload) VALUES (gen_random_uuid(), 'ExtractionConfirmed', ...);
COMMIT;
-- relay: SELECT ... FROM outbox WHERE published_at IS NULL FOR UPDATE SKIP LOCKED LIMIT 100;
-- publish to EventBridge / SQS; UPDATE outbox SET published_at = now()
```
Relay runs as a small ECS task or scheduled job; at-least-once delivery → consumers must be idempotent.

## 3. Idempotent consumer
Table `processed_messages(consumer, message_id, processed_at)` with unique key; skip if present. Side effects (S3 writes) use deterministic keys so repeats overwrite safely.

## 4. Retry, backoff, DLQ
SQS visibility timeout > max job time; `maxReceiveCount` 3–5 → DLQ; alarm on DLQ depth > 0; runbook to inspect and redrive. Client retries: exponential backoff with full jitter, cap 30 s, only for retryable errors (5xx, throttling, timeouts).

## 5. Circuit breaker + fallback
Per provider: open after ≥ 50% failures in 60 s (min 10 calls); half-open after 30 s. Fallbacks: secondary model, keep job queued with delay, or mark `needs_manual` (BR-019).

## 6. Bulkhead
Separate queues and worker services: `ocr-jobs` (CPU heavy) and `llm-jobs` (I/O, rate-limited). A slow LLM provider must not block OCR throughput.

## 7. Rate limiting & quotas
API: token bucket per user/IP in Redis. LLM: per-user daily token quota and global budget guard.

## 8. Saga (account deletion)
Steps: mark deleting → revoke sessions → delete S3 objects (versions) → delete DB rows / crypto-shred key → purge analytics rows by pseudo id → delete vectors → confirm. Each step idempotent; on failure, retry; after N failures → alert human; Step Functions is a good fit.

## 9. Adapter (ports & adapters)
```python
class OcrProvider(Protocol):
    async def recognize(self, image: bytes, lang_hints: list[str]) -> OcrResult: ...


class LlmProvider(Protocol):
    async def extract(self, text: str, schema: dict, prompt_version: str) -> ExtractionResult: ...
```
Implementations: `PaddleOcr`, `TextractOcr` (English only), `BedrockLlm`, `FakeLlm` for tests.

## 10. Caching
Cache unit configs and knowledge chunks (not PHI). Cache LLM extraction by `sha256(document)+prompt_version+model` to avoid repeat cost.

## 11. Feature flags
AppConfig flags: `unit.<code>.enabled`, `ai.model.<step>`, `viewer.3d.enabled`; evaluated server-side; changes audited.
