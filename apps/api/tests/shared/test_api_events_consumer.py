import json
import logging
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from medilens.core.db import make_engine, make_session_factory
from medilens.modules.document.domain.models import accepts_status
from medilens.shared.api_events_consumer import InvalidEvent, consume_once, handle, parse
from sqlalchemy import Engine, text

from tests.db.conftest import (  # noqa: F401  (Testcontainers fixtures)
    alembic_cfg,
    migrated_url,
    pg_url,
)

EXAMPLES = Path(__file__).resolve().parents[4] / "docs/architecture/contracts/examples"
PIPELINE = ["uploaded", "validated", "preprocessed", "classified", "ocr_done", "extracted"]


def event(doc: object, status: str, **extra: object) -> str:
    return json.dumps(
        {
            "schemaVersion": 1,
            "event": "document.status_changed",
            "documentId": str(doc),
            "status": status,
            **extra,
        }
    )


@pytest.fixture
def engine(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    eng = make_engine(migrated_url)
    yield eng
    eng.dispose()


def new_doc(engine: Engine, status: str) -> str:
    # NOTE: superuser connection bypasses RLS; the system-caller RLS path is an open point.
    with engine.begin() as c:
        uid = c.execute(
            text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
            {"s": str(uuid4())},
        ).scalar_one()
        pid = c.execute(
            text("INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) RETURNING id"),
            {"u": uid},
        ).scalar_one()
        return str(
            c.execute(
                text(
                    "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime, status)"
                    " VALUES (:p, 'k', '', 'image/png', :s) RETURNING id"
                ),
                {"p": pid, "s": status},
            ).scalar_one()
        )


def status_of(engine: Engine, doc: str) -> str:
    with engine.connect() as c:
        return c.execute(
            text("SELECT status FROM clinical.documents WHERE id = :i"), {"i": doc}
        ).scalar_one()


CASES = [
    # (stored, incoming, expected stored after)
    ("uploaded", "validated", "validated"),
    ("uploaded", "extracted", "extracted"),  # skipping ahead is still forward
    ("extracted", "needs_review", "needs_review"),
    ("validated", "validated", "validated"),  # duplicate
    ("classified", "validated", "classified"),  # regression
    ("needs_review", "extracted", "needs_review"),
    ("ocr_done", "needs_retake", "needs_retake"),
    ("validated", "failed", "failed"),
    ("needs_retake", "validated", "needs_retake"),  # terminals final
    ("needs_retake", "failed", "needs_retake"),
    ("failed", "needs_review", "failed"),
    ("rejected", "validated", "rejected"),
    ("rejected", "failed", "rejected"),
    ("needs_review", "confirmed", "needs_review"),  # confirmed never from events
    ("uploaded", "confirmed", "uploaded"),
    ("confirmed", "failed", "confirmed"),
]


@pytest.mark.parametrize(("stored", "incoming", "expected"), CASES)
def test_forward_only_matrix(engine: Engine, stored: str, incoming: str, expected: str) -> None:
    doc = new_doc(engine, stored)
    handle(event(doc, incoming), make_session_factory(engine))
    assert status_of(engine, doc) == expected


def test_domain_rule_matches_matrix() -> None:
    assert all(accepts_status(a, b) for a, b in zip(PIPELINE, PIPELINE[1:], strict=False))
    assert not accepts_status("extracted", "extracted")


def test_unknown_document_is_dropped_and_logs_id_only(
    engine: Engine, caplog: pytest.LogCaptureFixture
) -> None:
    ghost = uuid4()
    with caplog.at_level(logging.WARNING):
        out = handle(event(ghost, "validated", reason="x"), make_session_factory(engine))
    assert out == "unknown"
    assert str(ghost) in caplog.text


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        ("not json", "bad_json"),
        ("[]", "bad_json"),
        (json.dumps({"event": "extraction.completed"}), "unsupported_event"),
        (event(uuid4(), "rejected"), "schema_violation"),  # API-only status
        (event("not-a-uuid", "validated"), "schema_violation"),
        (event(uuid4(), "validated", reason="Blurry photo"), "schema_violation"),
        (event(uuid4(), "validated", extra="x"), "schema_violation"),
    ],
)
def test_invalid_messages_have_reason_codes(body: str, reason: str) -> None:
    with pytest.raises(InvalidEvent) as e:
        parse(body)
    assert e.value.reason == reason


def test_contract_examples() -> None:
    parse((EXAMPLES / "document-status-changed.valid.json").read_text())
    with pytest.raises(InvalidEvent):
        parse((EXAMPLES / "document-status-changed.invalid.json").read_text())


class FakeSqs:
    def __init__(self, bodies: list[str]) -> None:
        self.messages = [
            {"MessageId": f"m{i}", "ReceiptHandle": f"r{i}", "Body": b}
            for i, b in enumerate(bodies)
        ]
        self.deleted: list[str] = []

    def receive_message(self, **_: object) -> dict[str, object]:
        return {"Messages": self.messages}

    def delete_message(self, QueueUrl: str, ReceiptHandle: str) -> None:  # noqa: N803
        self.deleted.append(ReceiptHandle)


def test_delete_after_commit_and_invalid_left_for_dlq(engine: Engine) -> None:
    doc = new_doc(engine, "uploaded")
    sqs = FakeSqs([event(doc, "validated"), "garbage", event(uuid4(), "validated")])
    assert consume_once(sqs, "q", make_session_factory(engine)) == 2
    assert sqs.deleted == ["r0", "r2"]  # unknown id is dropped (deleted); garbage is not
    assert status_of(engine, doc) == "validated"
