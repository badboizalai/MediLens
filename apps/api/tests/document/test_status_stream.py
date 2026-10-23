import json
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from medilens.core.db import make_engine
from medilens.modules.document.api import router as doc_router
from medilens.modules.document.application.status_stream import (
    HEARTBEAT_SECONDS,
    MAX_STREAM_SECONDS,
    POLL_SECONDS,
    Clock,
    watch_status,
)
from sqlalchemy import text

from .conftest import Env
from .test_upload import request


class FakeClock:
    def __init__(self, on_sleep: Any = None) -> None:
        self.t = 0.0
        self.on_sleep = on_sleep

    def sleep(self, s: float) -> None:
        self.t += s
        if self.on_sleep:
            self.on_sleep()

    def clock(self) -> Clock:
        return Clock(self.sleep, lambda: self.t)


def test_watch_emits_changes_then_stops_on_terminal() -> None:
    seq = iter(["uploaded", "uploaded", "validated", "failed", "never"])
    assert list(watch_status(lambda: next(seq), FakeClock().clock())) == [
        "uploaded",
        "validated",
        "failed",
    ]


def test_watch_heartbeat_and_max_duration() -> None:
    fc = FakeClock()
    out = list(watch_status(lambda: "uploaded", fc.clock()))
    assert out[0] == "uploaded"
    assert out.count(None) == int(MAX_STREAM_SECONDS // HEARTBEAT_SECONDS)
    assert fc.t <= MAX_STREAM_SECONDS + POLL_SECONDS


def test_watch_ends_when_document_disappears() -> None:
    seq = iter(["uploaded", None])
    assert list(watch_status(lambda: next(seq), FakeClock().clock())) == ["uploaded"]


def test_stream_pushes_changes_and_closes_on_terminal(env: Env) -> None:
    doc_id = request(env).json()["document_id"]  # 'uploaded-pending'
    steps = iter(["validated", "ocr_done", "extracted", "needs_review"])

    def advance() -> None:
        engine = make_engine(env.url)
        with engine.begin() as c:
            c.execute(text("UPDATE clinical.documents SET status = :s"), {"s": next(steps)})
        engine.dispose()

    env.client.app.dependency_overrides[doc_router.get_clock] = (  # type: ignore[attr-defined]
        FakeClock(advance).clock
    )
    r = env.client.get(f"/v1/documents/{doc_id}/events")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.headers["cache-control"] == "no-cache"
    got = [
        json.loads(b.split("data: ", 1)[1])
        for b in r.text.strip().split("\n\n")
        if b.startswith("event: status\n")
    ]
    assert [e["status"] for e in got] == [
        "uploaded-pending",
        "validated",
        "ocr_done",
        "extracted",
        "needs_review",
    ]
    assert all("updatedAt" in e for e in got)


def test_stream_authz(env: Env) -> None:
    doc_id = request(env).json()["document_id"]
    env.as_user("bob")
    assert env.client.get(f"/v1/documents/{doc_id}/events").status_code == 404  # no leak
    assert env.client.get(f"/v1/documents/{uuid4()}/events").status_code == 404


def test_stream_unauthenticated_is_401() -> None:
    from medilens.main import create_app

    r = TestClient(create_app()).get(f"/v1/documents/{uuid4()}/events")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
