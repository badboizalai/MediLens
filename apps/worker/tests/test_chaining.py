import json
from pathlib import Path

from jsonschema import Draft202012Validator
from medilens_worker.intake.validate import ScanPending
from medilens_worker.jobs.registry import REGISTRY, JobSpec
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.runner import RetryPolicy, handle
from medilens_worker.pipeline.state import DocStatus, NonRetryable, StatusRepo
from medilens_worker.queue.events import InMemoryEventSink
from medilens_worker.queue.memory import InMemoryQueue

C = Path(__file__).parents[3] / "docs/architecture/contracts"
JOB = Draft202012Validator(json.loads((C / "job-message.schema.json").read_text()))
EVT = Draft202012Validator(json.loads((C / "document-status-changed.schema.json").read_text()))
DOC = "11111111-1111-4111-8111-111111111111"
S = DocStatus


def reg(**handlers):
    return {t: JobSpec(handlers.get(t, lambda c: None), r.src, r.dst) for t, r in REGISTRY.items()}


def env():
    return InMemoryQueue(), StatusRepo(), InMemoryIdempotencyStore(), InMemoryEventSink()


def drain(q, st, store, ev, registry, policy=None):
    out = []
    while (m := q.receive()) is not None:
        JOB.validate(json.loads(m.body))
        out.append(handle(q, m, st, store, policy or RetryPolicy(), registry, ev))
        q.make_all_visible()
    return out


def start(q, **extra):
    q.send(json.dumps({"type": "document.validate", "documentId": DOC, "attempt": 1, **extra}))


def test_full_chain_and_events_match_schemas():
    q, st, store, ev = env()
    start(q)
    assert drain(q, st, store, ev, reg()) == ["done"] * 6
    assert st.get(DOC) == S.NEEDS_REVIEW
    assert [e["status"] for e in ev.events] == [
        s.dst.value for s in REGISTRY.values()
    ]  # registry order == pipeline order
    for e in ev.events:
        EVT.validate(e)


def test_chained_message_has_ids_only():
    q, st, store, ev = env()
    start(q, storageKey=f"quarantine/{DOC}/{DOC}", mime="image/png")
    handle(q, q.receive(), st, store, registry=reg(), events=ev)
    assert json.loads(q.receive().body) == {
        "type": "document.preprocess",
        "documentId": DOC,
        "attempt": 1,
    }


def test_duplicate_delivery_rechains_and_reemits():
    q, st, store, ev = env()
    st.set(DOC, S.VALIDATED)  # crashed after set, before send
    start(q)
    assert handle(q, q.receive(), st, store, registry=reg(), events=ev) == "duplicate"
    assert json.loads(q.receive().body)["type"] == "document.preprocess"
    assert ev.events[0]["status"] == "validated"


def test_terminal_events_carry_reason_codes():
    class Blurry(NonRetryable):
        status, reason = S.NEEDS_RETAKE, "blurry"

    def boom(c):
        raise Blurry

    q, st, store, ev = env()
    start(q)
    assert drain(q, st, store, ev, reg(**{"document.preprocess": boom})) == ["done", "terminal"]
    assert ev.events[1:] == [
        {
            "event": "document.status_changed",
            "schemaVersion": 1,
            "documentId": DOC,
            "status": "needs_retake",
            "reason": "blurry",
        }
    ]
    EVT.validate(ev.events[1])


def test_max_attempts_emits_failed():
    def boom(c):
        raise RuntimeError("x")

    q, st, store, ev = env()
    start(q)
    r = reg(**{"document.validate": boom})
    assert drain(q, st, store, ev, r, RetryPolicy(max_attempts=2)) == ["retry", "dlq"]
    EVT.validate(ev.events[-1])
    assert (ev.events[-1]["status"], ev.events[-1]["reason"]) == ("failed", "max_attempts")


def test_scan_pending_has_its_own_budget():
    def pending(c):
        raise ScanPending("malware_scan_pending")

    q, st, store, ev = env()
    start(q)
    outcomes = drain(q, st, store, ev, reg(**{"document.validate": pending}))
    assert outcomes == ["retry"] * 19 + ["dlq"]  # not the normal 3 attempts
    assert set(q.sent_delays[1:]) == {ScanPending.delay_seconds}
