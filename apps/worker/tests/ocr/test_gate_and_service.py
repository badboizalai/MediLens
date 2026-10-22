"""Pure-logic tests: run without the `ocr` extra."""

import json

import pytest
from medilens_worker.jobs.registry import REGISTRY
from medilens_worker.ocr import service
from medilens_worker.ocr.engine import FakeOcrEngine
from medilens_worker.ocr.gate import decide, quality_score
from medilens_worker.ocr.service import InMemoryPageStore
from medilens_worker.ocr.types import Metrics, PreprocessedPage, RetakeReason
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.runner import RetryPolicy, handle
from medilens_worker.pipeline.state import DocStatus, StatusRepo
from medilens_worker.queue.memory import InMemoryQueue

GOOD = Metrics(blur=400.0, brightness=150.0, ink_ratio=0.05)


@pytest.mark.parametrize(
    ("m", "expected"),
    [
        (GOOD, None),
        (Metrics(30.0, 150.0, 0.05), RetakeReason.BLURRY),
        (Metrics(400.0, 30.0, 0.05), RetakeReason.TOO_DARK),
        (Metrics(400.0, 150.0, 0.0), RetakeReason.NOT_A_DOCUMENT),
        (Metrics(400.0, 150.0, 0.9), RetakeReason.NOT_A_DOCUMENT),
        (Metrics(30.0, 30.0, 0.05), RetakeReason.TOO_DARK),  # lighting reported before focus
    ],
)
def test_decide(m, expected):
    assert decide(m) == expected


def test_retake_codes_are_stable_strings():
    assert {r.value for r in RetakeReason} == {"blurry", "too_dark", "not_a_document"}


def test_quality_score_bounds_and_order():
    assert 0.0 <= quality_score(Metrics(0, 0, 0.05)) <= 1.0
    assert quality_score(GOOD) > quality_score(Metrics(60.0, 150.0, 0.05))
    assert quality_score(GOOD) > 0.95


def _pre(n):
    return PreprocessedPage(n, b"png", 0.9, GOOD)


def test_run_ocr_produces_text_boxes_quality():
    store = InMemoryPageStore()
    store.save_preprocessed("d1", [_pre(1), _pre(2)])
    engine, ext = FakeOcrEngine(["a", "b"]), []
    service.run_ocr("d1", store, engine, ext.append)
    pages = store.ocr["d1"]
    assert [p.page for p in pages] == [1, 2]
    assert pages[0].text == "a\nb" and len(pages[0].boxes) == 2 and pages[0].quality == 0.9
    assert engine.calls == 2 and ext == [120, 120]


def test_run_ocr_without_pages_fails():
    with pytest.raises(LookupError):
        service.run_ocr("nope", InMemoryPageStore(), FakeOcrEngine())


def test_ocr_handler_wired_in_registry():
    assert REGISTRY["document.ocr"].src == DocStatus.CLASSIFIED
    store = InMemoryPageStore()
    store.save_preprocessed("d1", [_pre(1)])
    service.configure(store, FakeOcrEngine(["x"]))
    q, st = InMemoryQueue(), StatusRepo()
    for s in (DocStatus.VALIDATED, DocStatus.PREPROCESSED, DocStatus.CLASSIFIED):
        st.set("d1", s)
    q.send(json.dumps({"type": "document.ocr", "documentId": "d1", "attempt": 1}))
    assert handle(q, q.receive(), st, InMemoryIdempotencyStore()) == "done"
    assert st.get("d1") == DocStatus.OCR_DONE
    assert store.ocr["d1"][0].text == "x"
    assert q.extensions[0][1] == 120


def test_retake_failure_is_not_silently_ok():
    """Without pages the preprocess handler fails (retry -> DLQ), never advances."""
    service.configure(InMemoryPageStore())
    q, st = InMemoryQueue(), StatusRepo()
    st.set("d9", DocStatus.VALIDATED)
    q.send(json.dumps({"type": "document.preprocess", "documentId": "d9", "attempt": 1}))
    pol = RetryPolicy(max_attempts=1)
    assert handle(q, q.receive(), st, InMemoryIdempotencyStore(), pol) == "dlq"
    assert st.get("d9") == DocStatus.FAILED
