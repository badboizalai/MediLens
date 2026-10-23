import json

import pytest
from medilens_worker.jobs.registry import JobSpec
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.runner import RetryPolicy, handle
from medilens_worker.pipeline.state import (
    DocStatus,
    InvalidTransition,
    StatusRepo,
    guard_transition,
)
from medilens_worker.queue.memory import InMemoryQueue


def body(type_="document.validate", doc="d1", attempt=1):
    return json.dumps({"type": type_, "documentId": doc, "attempt": attempt})


@pytest.fixture
def env():
    return InMemoryQueue(), StatusRepo(), InMemoryIdempotencyStore()


def test_guard_allows_and_rejects():
    assert guard_transition(DocStatus.UPLOADED, DocStatus.VALIDATED) == DocStatus.VALIDATED
    with pytest.raises(InvalidTransition):
        guard_transition(DocStatus.UPLOADED, DocStatus.EXTRACTED)
    with pytest.raises(InvalidTransition):
        guard_transition(DocStatus.FAILED, DocStatus.VALIDATED)


def test_happy_path_and_idempotent_redelivery(env):
    q, st, store = env
    q.send(body())
    assert handle(q, q.receive(), st, store) == "done"
    assert st.get("d1") == DocStatus.VALIDATED
    q.send(body())  # same doc/step/attempt delivered again
    assert handle(q, q.receive(), st, store) == "duplicate"
    assert st.get("d1") == DocStatus.VALIDATED


def test_retry_with_backoff_then_dlq(env):
    q, st, store = env
    calls = []

    def boom(ctx):
        calls.append(ctx.attempt)
        raise RuntimeError("patient name leak")

    reg = {"document.validate": JobSpec(boom, DocStatus.UPLOADED, DocStatus.VALIDATED)}
    pol = RetryPolicy(max_attempts=3, base_seconds=5)
    q.send(body())
    outcomes = []
    for _ in range(3):
        outcomes.append(handle(q, q.receive(), st, store, pol, reg))
        q.make_all_visible()
    assert outcomes == ["retry", "retry", "dlq"]
    assert calls == [1, 2, 3]
    assert q.sent_delays[1:] == [5, 10]
    assert q.dlq[0][1].startswith("max_attempts")
    assert "patient" not in q.dlq[0][1]
    assert st.get("d1") == DocStatus.FAILED


def test_unknown_job_type_dlq(env):
    q, st, store = env
    q.send(body("document.nope"))
    assert handle(q, q.receive(), st, store) == "dlq"
    assert q.dlq[0][1] == "unknown_job_type"


@pytest.mark.parametrize("raw", ["not json", "[]", json.dumps({"type": "document.ocr"})])
def test_poison_message_dlq(env, raw):
    q, st, store = env
    q.send(raw)
    assert handle(q, q.receive(), st, store) == "dlq"
    assert q.dlq[0][1] == "poison_message"
    assert q.receive() is None


def test_wrong_state_is_retried_not_applied(env):
    q, st, store = env
    q.send(body("document.ocr"))  # doc is still UPLOADED
    assert handle(q, q.receive(), st, store) == "retry"
    assert st.get("d1") == DocStatus.UPLOADED


def test_visibility_extension(env):
    q, st, store = env

    def slow(ctx):
        ctx.extend_visibility(120)

    reg = {"document.validate": JobSpec(slow, DocStatus.UPLOADED, DocStatus.VALIDATED)}
    q.send(body())
    handle(q, q.receive(), st, store, registry=reg)
    assert q.extensions[0][1] == 120


def test_held_lease_leaves_message_and_failure_releases(env):
    q, st, store = env
    store.claim("d1:document.validate:1")  # another worker is mid-flight
    q.send(body())
    assert handle(q, q.receive(), st, store) == "in_progress"
    assert st.get("d1") == DocStatus.UPLOADED


def test_handler_failure_releases_lease(env):
    q, st, store = env

    def boom(ctx):
        raise RuntimeError("x")

    reg = {"document.validate": JobSpec(boom, DocStatus.UPLOADED, DocStatus.VALIDATED)}
    q.send(body())
    assert handle(q, q.receive(), st, store, registry=reg) == "retry"
    assert store.claim("d1:document.validate:1")
