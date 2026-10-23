"""Process one queue message: parse, dedup, guard, run, retry/DLQ."""

import json
import logging
from dataclasses import dataclass

from medilens_worker.jobs.registry import REGISTRY, JobContext, JobSpec
from medilens_worker.pipeline.idempotency import IdempotencyStore, dedup_key
from medilens_worker.pipeline.state import DocStatus, NonRetryable, StatusRepo
from medilens_worker.queue.base import Message, Queue

log = logging.getLogger("medilens_worker")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_seconds: int = 5
    cap_seconds: int = 300

    def delay(self, attempt: int) -> int:
        return min(self.base_seconds * 2 ** (attempt - 1), self.cap_seconds)


DEFAULT_POLICY = RetryPolicy()


def _event(event: str, **fields: object) -> None:
    # IDs, step names and reasons only. Never log payloads or exception text (may hold PHI).
    log.info(json.dumps({"event": event, **fields}, sort_keys=True))


def _parse(body: str) -> dict:
    d = json.loads(body)
    if not (
        isinstance(d, dict)
        and isinstance(d.get("type"), str)
        and isinstance(d.get("documentId"), str)
        and isinstance(d.get("attempt", 1), int)
    ):
        raise ValueError("bad shape")
    return d


def handle(
    queue: Queue,
    msg: Message,
    statuses: StatusRepo,
    store: IdempotencyStore,
    policy: RetryPolicy = DEFAULT_POLICY,
    registry: dict[str, JobSpec] = REGISTRY,
) -> str:
    """Returns outcome: done | duplicate | in_progress | retry | dlq | terminal."""
    try:
        d = _parse(msg.body)
    except ValueError:  # includes JSONDecodeError
        queue.send_dlq(msg, "poison_message")
        _event("dlq", reason="poison_message")
        return "dlq"

    step, doc_id, attempt = d["type"], d["documentId"], d.get("attempt", 1)
    spec = registry.get(step)
    if spec is None:
        queue.send_dlq(msg, "unknown_job_type")
        _event("dlq", reason="unknown_job_type", step=step, document_id=doc_id)
        return "dlq"

    key = dedup_key(doc_id, step, attempt)
    if store.seen(key) or statuses.get(doc_id) == spec.dst:
        queue.ack(msg)
        _event("duplicate", step=step, document_id=doc_id, attempt=attempt)
        return "duplicate"
    if not store.claim(key):  # another worker holds the lease: leave the message to redeliver
        _event("in_progress", step=step, document_id=doc_id, attempt=attempt)
        return "in_progress"

    try:
        if statuses.get(doc_id) != spec.src:
            raise RuntimeError("invalid_state")
        spec.handler(JobContext(doc_id, attempt, lambda s: queue.extend_visibility(msg, s)))
        statuses.set(doc_id, spec.dst)
    except NonRetryable as out:
        statuses.set(doc_id, out.status)
        statuses.reasons[doc_id] = out.reason
        store.mark(key)
        queue.ack(msg)
        _event(
            "terminal", step=step, document_id=doc_id, status=out.status.value, reason=out.reason
        )
        return "terminal"
    except Exception as exc:  # noqa: BLE001 - boundary: any handler failure is retried
        store.release(key)
        reason = type(exc).__name__
        if attempt < policy.max_attempts:
            queue.send(json.dumps({**d, "attempt": attempt + 1}), policy.delay(attempt))
            queue.ack(msg)
            _event("retry", step=step, document_id=doc_id, attempt=attempt, reason=reason)
            return "retry"
        if statuses.get(doc_id) not in (DocStatus.FAILED, DocStatus.CONFIRMED):
            statuses.set(doc_id, DocStatus.FAILED)
        queue.send_dlq(msg, f"max_attempts:{reason}")
        _event("dlq", reason="max_attempts", step=step, document_id=doc_id, attempt=attempt)
        return "dlq"

    store.mark(key)
    queue.ack(msg)
    _event("done", step=step, document_id=doc_id, attempt=attempt, status=spec.dst.value)
    return "done"
