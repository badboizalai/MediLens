"""Process one queue message: parse, dedup, guard, run, retry/DLQ."""

import json
import logging
from dataclasses import dataclass

from medilens_worker.jobs.registry import REGISTRY, JobContext, JobSpec
from medilens_worker.pipeline.idempotency import IdempotencyStore, dedup_key
from medilens_worker.pipeline.state import DocStatus, NonRetryable, RetryLater, StatusRepo
from medilens_worker.queue.base import Message, Queue
from medilens_worker.queue.events import EventSink, InMemoryEventSink

log = logging.getLogger("medilens_worker")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_seconds: int = 5
    cap_seconds: int = 300

    def delay(self, attempt: int) -> int:
        return min(self.base_seconds * 2 ** (attempt - 1), self.cap_seconds)


DEFAULT_POLICY = RetryPolicy()
_STOP = (DocStatus.NEEDS_RETAKE, DocStatus.FAILED)  # terminal: never run or overwrite


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


def _emit(events: EventSink, doc_id: str, status: DocStatus, reason: str | None = None) -> None:
    ev: dict = {
        "event": "document.status_changed",
        "schemaVersion": 1,
        "documentId": doc_id,
        "status": status.value,
    }
    if reason:
        ev["reason"] = reason
    events(ev)


def _chain(queue: Queue, registry: dict[str, JobSpec], doc_id: str, dst: DocStatus) -> None:
    # ids only: the schema forbids storageKey/mime outside document.validate
    nxt = next((t for t, sp in registry.items() if sp.src == dst), None)
    if nxt:
        queue.send(json.dumps({"type": nxt, "documentId": doc_id, "attempt": 1}))


def handle(
    queue: Queue,
    msg: Message,
    statuses: StatusRepo,
    store: IdempotencyStore,
    policy: RetryPolicy = DEFAULT_POLICY,
    registry: dict[str, JobSpec] = REGISTRY,
    events: EventSink | None = None,
) -> str:
    """Returns outcome: done | duplicate | in_progress | retry | dlq | terminal."""
    try:
        d = _parse(msg.body)
    except ValueError:  # includes JSONDecodeError
        queue.send_dlq(msg, "poison_message")
        _event("dlq", reason="poison_message")
        return "dlq"

    events = events or InMemoryEventSink()
    step, doc_id, attempt = d["type"], d["documentId"], d.get("attempt", 1)
    spec = registry.get(step)
    if spec is None:
        queue.send_dlq(msg, "unknown_job_type")
        _event("dlq", reason="unknown_job_type", step=step, document_id=doc_id)
        return "dlq"

    key = dedup_key(doc_id, step, attempt)
    if store.seen(key) or statuses.get(doc_id) == spec.dst:
        if statuses.get(doc_id) == spec.dst:  # a crash may have lost the event or the next step
            _emit(events, doc_id, spec.dst)
            _chain(queue, registry, doc_id, spec.dst)
        queue.ack(msg)
        _event("duplicate", step=step, document_id=doc_id, attempt=attempt)
        return "duplicate"
    if statuses.get(doc_id) in _STOP:  # e.g. a redelivery after the sink failed mid-terminal
        queue.ack(msg)
        _event("terminal", step=step, document_id=doc_id, status=statuses.get(doc_id).value)
        return "terminal"
    # step-level lease (attempt 0) so a re-chained attempt 1 cannot run beside a live retry
    step_lease = dedup_key(doc_id, step, 0)
    if not store.claim(key):  # another worker holds the lease: leave the message to redeliver
        _event("in_progress", step=step, document_id=doc_id, attempt=attempt)
        return "in_progress"
    if not store.claim(step_lease):
        store.release(key)
        _event("in_progress", step=step, document_id=doc_id, attempt=attempt)
        return "in_progress"

    try:
        return _run(queue, msg, d, spec, statuses, store, policy, registry, events, key)
    finally:
        store.release(step_lease)


def _run(queue, msg, d, spec, statuses, store, policy, registry, events, key) -> str:
    step, doc_id, attempt = d["type"], d["documentId"], d.get("attempt", 1)
    try:
        if statuses.get(doc_id) != spec.src:
            raise RuntimeError("invalid_state")
        spec.handler(JobContext(doc_id, attempt, lambda s: queue.extend_visibility(msg, s), d))
        statuses.set(doc_id, spec.dst)
        _emit(events, doc_id, spec.dst)
        _chain(queue, registry, doc_id, spec.dst)
    except NonRetryable as out:
        statuses.set(doc_id, out.status)
        statuses.reasons[doc_id] = out.reason
        _emit(events, doc_id, out.status, out.reason)
        store.mark(key)
        queue.ack(msg)
        _event(
            "terminal", step=step, document_id=doc_id, status=out.status.value, reason=out.reason
        )
        return "terminal"
    except Exception as exc:  # noqa: BLE001 - boundary: any handler failure is retried
        store.release(key)
        reason = type(exc).__name__
        max_attempts = exc.max_attempts if isinstance(exc, RetryLater) else policy.max_attempts
        if attempt < max_attempts:
            delay = exc.delay_seconds if isinstance(exc, RetryLater) else policy.delay(attempt)
            queue.send(json.dumps({**d, "attempt": attempt + 1}), delay)
            queue.ack(msg)
            _event("retry", step=step, document_id=doc_id, attempt=attempt, reason=reason)
            return "retry"
        if statuses.get(doc_id) not in (*_STOP, DocStatus.CONFIRMED):
            statuses.set(doc_id, DocStatus.FAILED)
            _emit(events, doc_id, DocStatus.FAILED, "max_attempts")
        queue.send_dlq(msg, f"max_attempts:{reason}")
        _event("dlq", reason="max_attempts", step=step, document_id=doc_id, attempt=attempt)
        return "dlq"

    store.mark(key)
    queue.ack(msg)
    _event("done", step=step, document_id=doc_id, attempt=attempt, status=spec.dst.value)
    return "done"
