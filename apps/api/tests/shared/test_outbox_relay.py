import json
from collections.abc import Iterator

import pytest
from medilens.core.db import make_engine
from medilens.shared.outbox_relay import relay_once
from sqlalchemy import Engine, text

from tests.db.conftest import (  # noqa: F401  (Testcontainers fixtures)
    alembic_cfg,
    migrated_url,
    pg_url,
)

DOC = "0190a000-0000-7000-8000-000000000001"
KEY = "quarantine/p1/" + DOC


@pytest.fixture
def engine(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    eng = make_engine(migrated_url)
    yield eng
    eng.dispose()


def add(engine: Engine, event_type: str = "DocumentUploaded") -> None:
    payload = {"document_id": DOC, "profile_id": "p1", "mime": "image/png", "storage_key": KEY}
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO clinical.outbox (event_type, payload) VALUES (:t, CAST(:p AS jsonb))"
            ),
            {"t": event_type, "p": json.dumps(payload)},
        )


def unpublished(engine: Engine) -> int:
    with engine.connect() as c:
        return c.execute(
            text("SELECT count(*) FROM clinical.outbox WHERE published_at IS NULL")
        ).scalar_one()


def test_publishes_job_message_and_marks_row(engine: Engine) -> None:
    add(engine)
    sent: list[str] = []
    assert relay_once(engine, sent.append) == 1
    assert [json.loads(b) for b in sent] == [
        {
            "type": "document.validate",
            "documentId": DOC,
            "storageKey": KEY,
            "mime": "image/png",
            "attempt": 1,
        }
    ]
    assert unpublished(engine) == 0


def test_second_run_publishes_nothing(engine: Engine) -> None:
    add(engine)
    relay_once(engine, lambda _b: None)
    sent: list[str] = []
    assert relay_once(engine, sent.append) == 0 and sent == []


def test_publish_failure_keeps_row(engine: Engine) -> None:
    add(engine)

    def boom(_body: str) -> None:
        raise RuntimeError("sqs down")

    with pytest.raises(RuntimeError):
        relay_once(engine, boom)
    assert unpublished(engine) == 1
    sent: list[str] = []
    assert relay_once(engine, sent.append) == 1  # retried later


def test_unknown_type_is_skipped_and_logged_without_payload(
    engine: Engine, caplog: pytest.LogCaptureFixture
) -> None:
    add(engine, "Mystery")
    sent: list[str] = []
    with caplog.at_level("WARNING"):
        assert relay_once(engine, sent.append) == 0
    assert sent == [] and unpublished(engine) == 1
    assert "Mystery" in caplog.text and KEY not in caplog.text
