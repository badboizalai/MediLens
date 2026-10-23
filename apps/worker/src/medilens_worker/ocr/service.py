"""Preprocess and OCR steps over a page store. Storage (S3/DB) is injected; none lives here."""

import os
from collections.abc import Callable
from typing import Protocol

from medilens_worker.ocr.engine import FakeOcrEngine, OcrEngine
from medilens_worker.ocr.types import OcrPage, PreprocessedPage, RetakeReason, RetakeRequired


class PageStore(Protocol):
    def raw_pages(self, document_id: str) -> list[bytes]: ...
    def save_preprocessed(self, document_id: str, pages: list[PreprocessedPage]) -> None: ...
    def preprocessed(self, document_id: str) -> list[PreprocessedPage]: ...
    def save_ocr(self, document_id: str, pages: list[OcrPage]) -> None: ...
    def ocr_pages(self, document_id: str) -> list[OcrPage]: ...
    def save_retake(self, document_id: str, page: int, reason: RetakeReason) -> None: ...


class InMemoryPageStore:
    def __init__(self, raw: dict[str, list[bytes]] | None = None) -> None:
        self.raw = raw or {}
        self.pre: dict[str, list[PreprocessedPage]] = {}
        self.ocr: dict[str, list[OcrPage]] = {}
        self.retakes: dict[str, tuple[int, RetakeReason]] = {}

    def raw_pages(self, document_id: str) -> list[bytes]:
        return self.raw.get(document_id, [])

    def save_preprocessed(self, document_id: str, pages: list[PreprocessedPage]) -> None:
        self.pre[document_id] = pages

    def preprocessed(self, document_id: str) -> list[PreprocessedPage]:
        return self.pre.get(document_id, [])

    def save_ocr(self, document_id: str, pages: list[OcrPage]) -> None:
        self.ocr[document_id] = pages

    def ocr_pages(self, document_id: str) -> list[OcrPage]:
        return self.ocr.get(document_id, [])

    def save_retake(self, document_id: str, page: int, reason: RetakeReason) -> None:
        self.retakes[document_id] = (page, reason)


def run_preprocess(document_id: str, store: PageStore) -> None:
    """Gate every page; on the first failure persist its retake code and raise RetakeRequired."""
    from medilens_worker.ocr.preprocess import preprocess_page  # noqa: PLC0415 (needs `ocr` extra)

    raw = store.raw_pages(document_id)
    if not raw:
        raise LookupError("no_pages")
    done: list[PreprocessedPage] = []
    for n, data in enumerate(raw, start=1):
        page, reason = preprocess_page(n, data)
        if page is None:
            assert reason is not None
            store.save_retake(document_id, n, reason)
            raise RetakeRequired(n, reason)
        done.append(page)
    store.save_preprocessed(document_id, done)


def run_ocr(
    document_id: str,
    store: PageStore,
    engine: OcrEngine,
    extend_visibility: Callable[[int], None] = lambda s: None,
) -> None:
    pages = store.preprocessed(document_id)
    if not pages:
        raise LookupError("no_pages")
    out = []
    for p in pages:
        extend_visibility(120)  # long step: keep the message invisible between pages
        boxes = engine.recognize(p.image)
        out.append(OcrPage(p.page, "\n".join(b.text for b in boxes), boxes, p.quality))
    store.save_ocr(document_id, out)


# Wiring seam: main.py / tests swap these. Defaults are in-memory until S3/DB stores land.
_store: PageStore = InMemoryPageStore()
_engine: OcrEngine | None = None


def configure(store: PageStore | None = None, engine: OcrEngine | None = None) -> None:
    global _store, _engine
    _store = store or _store
    _engine = engine or _engine


def get_store() -> PageStore:
    return _store


def get_engine() -> OcrEngine:
    global _engine
    if _engine is None:
        if os.environ.get("WORKER_OCR_ENGINE", "paddle-vietocr") == "fake":
            _engine = FakeOcrEngine()
        else:
            from medilens_worker.ocr.adapters import PaddleVietOcrEngine  # noqa: PLC0415

            _engine = PaddleVietOcrEngine()
    return _engine
