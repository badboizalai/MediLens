"""Ports the extract handler needs; wired by the app (OCR text store, run store, gateway)."""

from collections.abc import Callable
from dataclasses import dataclass

from medilens_worker.queue.events import EventSink

from .service import ExtractionRun, GatewayClient


@dataclass
class ExtractDeps:
    load_pages: Callable[[str], list[str]]  # document_id -> OCR text per page
    client: GatewayClient
    save_run: Callable[[ExtractionRun], None]
    load_run: Callable[[str], ExtractionRun | None]  # document_id -> latest saved run
    emit: EventSink  # api-events: extraction.completed
    unit_for: Callable[[str], str | None] = lambda document_id: None  # None => classify


_deps: ExtractDeps | None = None


def configure(deps: ExtractDeps | None) -> None:
    global _deps
    _deps = deps


def get_deps() -> ExtractDeps:
    if _deps is None:
        raise RuntimeError("extraction deps not configured")
    return _deps
