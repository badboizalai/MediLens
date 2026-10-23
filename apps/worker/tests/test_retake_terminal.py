import json

import pytest
from medilens_worker.jobs.registry import JobSpec
from medilens_worker.ocr.types import RetakeReason, RetakeRequired
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.runner import handle
from medilens_worker.pipeline.state import (
    DocStatus,
    InvalidTransition,
    StatusRepo,
    guard_transition,
)
from medilens_worker.queue.memory import InMemoryQueue


def _run(reason: RetakeReason, start: DocStatus):
    def gate_fail(ctx):
        raise RetakeRequired(1, reason)

    reg = {"document.preprocess": JobSpec(gate_fail, DocStatus.VALIDATED, DocStatus.PREPROCESSED)}
    q, st = InMemoryQueue(), StatusRepo()
    st.set("d1", DocStatus.VALIDATED)
    if start == DocStatus.PREPROCESSED:
        st.set("d1", start)
        reg = {"document.preprocess": JobSpec(gate_fail, start, DocStatus.CLASSIFIED)}
    q.send(json.dumps({"type": "document.preprocess", "documentId": "d1", "attempt": 1}))
    outcome = handle(q, q.receive(), st, InMemoryIdempotencyStore(), registry=reg)
    return outcome, q, st


@pytest.mark.parametrize("reason", list(RetakeReason))
def test_gate_failure_is_terminal_not_retried(reason):
    outcome, q, st = _run(reason, DocStatus.VALIDATED)
    assert outcome == "terminal"
    assert st.get("d1") == DocStatus.NEEDS_RETAKE
    assert st.reasons["d1"] == reason.value
    assert q.dlq == []
    assert q.receive() is None  # acked, nothing re-enqueued
    assert q.sent_delays == [0]  # only the original send, no retry


def test_needs_retake_only_reachable_before_ocr_and_reuploadable():
    assert guard_transition(DocStatus.NEEDS_RETAKE, DocStatus.UPLOADED) == DocStatus.UPLOADED
    with pytest.raises(InvalidTransition):
        guard_transition(DocStatus.NEEDS_RETAKE, DocStatus.VALIDATED)
    with pytest.raises(InvalidTransition):
        guard_transition(DocStatus.CLASSIFIED, DocStatus.NEEDS_RETAKE)


@pytest.mark.parametrize("status", [DocStatus.NEEDS_RETAKE, DocStatus.FAILED])
def test_job_for_terminal_document_is_noop(status):
    ran = []
    reg = {"document.preprocess": JobSpec(ran.append, DocStatus.VALIDATED, DocStatus.PREPROCESSED)}
    q, st = InMemoryQueue(), StatusRepo()
    st.set("d1", DocStatus.VALIDATED)
    st.set("d1", status)
    q.send(json.dumps({"type": "document.preprocess", "documentId": "d1", "attempt": 1}))
    assert handle(q, q.receive(), st, InMemoryIdempotencyStore(), registry=reg) == "terminal"
    assert ran == [] and st.get("d1") == status
    assert q.receive() is None and q.dlq == [] and q.sent_delays == [0]


def test_rechained_attempt1_does_not_race_running_retry():
    ran = []
    reg = {"document.preprocess": JobSpec(ran.append, DocStatus.VALIDATED, DocStatus.PREPROCESSED)}
    q, st, store = InMemoryQueue(), StatusRepo(), InMemoryIdempotencyStore()
    st.set("d1", DocStatus.VALIDATED)
    assert store.claim("d1:document.preprocess:0")  # retry attempt 2 holds the step lease
    q.send(json.dumps({"type": "document.preprocess", "documentId": "d1", "attempt": 1}))
    assert handle(q, q.receive(), st, store, registry=reg) == "in_progress"
    assert ran == [] and st.get("d1") == DocStatus.VALIDATED
