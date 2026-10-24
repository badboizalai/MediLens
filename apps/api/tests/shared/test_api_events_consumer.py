import json
import logging
from collections.abc import Iterator
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from medilens.core.db import make_engine, make_session_factory
from medilens.modules.document.infra.sql_repository import SqlDocumentRepository
from medilens.shared.api_events_consumer import InvalidEvent, consume_once, handle, parse
from sqlalchemy import Engine, text
from sqlalchemy import event as sa_event
from sqlalchemy.exc import ProgrammingError

from tests.db.conftest import (  # noqa: F401  (Testcontainers fixtures)
    alembic_cfg,
    migrated_url,
    pg_url,
)

EXAMPLES = Path(__file__).resolve().parents[4] / "docs/architecture/contracts/examples"


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
def admin(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    """Superuser: seeding and assertions only."""
    eng = make_engine(migrated_url)
    yield eng
    eng.dispose()


@pytest.fixture
def engine(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    """The consumer's view: non-superuser, no app.profile_ids, so RLS cannot hide problems."""
    eng = make_engine(migrated_url)

    @sa_event.listens_for(eng, "begin")
    def _as_consumer(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE api_events_consumer")

    yield eng
    eng.dispose()


def new_doc(engine: Engine, status: str, profile: str | None = None) -> str:
    with engine.begin() as c:
        uid = c.execute(
            text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
            {"s": str(uuid4())},
        ).scalar_one()
        pid = (
            profile
            or c.execute(
                text(
                    "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) RETURNING id"
                ),
                {"u": uid},
            ).scalar_one()
        )
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
def test_forward_only_matrix(
    admin: Engine, engine: Engine, stored: str, incoming: str, expected: str
) -> None:
    doc = new_doc(admin, stored)  # any profile, consumer sets no app.profile_ids
    handle(event(doc, incoming), make_session_factory(engine))
    assert status_of(admin, doc) == expected


def test_unknown_document_is_dropped_and_logs_id_only(
    engine: Engine, caplog: pytest.LogCaptureFixture
) -> None:
    ghost = uuid4()
    with caplog.at_level(logging.WARNING):
        out = handle(event(ghost, "validated", reason="x"), make_session_factory(engine))
    assert out == "unknown"
    assert str(ghost) in caplog.text


def test_outcomes(admin: Engine, engine: Engine) -> None:
    doc = new_doc(admin, "uploaded")
    sf = make_session_factory(engine)
    outs = []
    for st in ("validated", "validated", "confirmed"):
        with sf.begin() as ses:
            outs.append(SqlDocumentRepository(ses).apply_status(UUID(doc), st))
    assert outs == ["applied", "ignored", "ignored"]


def test_consumer_role_has_no_table_access(engine: Engine) -> None:
    for sql in ("SELECT 1 FROM clinical.documents", "UPDATE clinical.documents SET status='x'"):
        with pytest.raises(ProgrammingError, match="permission denied"), engine.begin() as c:
            c.execute(text(sql))


def test_app_rw_cannot_execute_function(admin: Engine) -> None:
    with pytest.raises(ProgrammingError, match="permission denied"), admin.begin() as c:
        c.exec_driver_sql("SET LOCAL ROLE app_rw")
        c.execute(text("SELECT clinical.apply_document_status(gen_random_uuid(), 'validated')"))


def test_function_changes_only_status(admin: Engine, engine: Engine) -> None:
    doc = new_doc(admin, "uploaded")
    cols = "profile_id, storage_key, sha256, mime, pages, doc_type, deleted_at, uploaded_at"
    with admin.connect() as c:
        before = c.execute(
            text(f"SELECT {cols} FROM clinical.documents WHERE id=:i"), {"i": doc}
        ).one()
    handle(event(doc, "validated"), make_session_factory(engine))
    with admin.connect() as c:
        after = c.execute(
            text(f"SELECT {cols} FROM clinical.documents WHERE id=:i"), {"i": doc}
        ).one()
    assert after == before


@pytest.mark.parametrize(
    ("body", "reason"),
    [
        ("not json", "bad_json"),
        ("[]", "bad_json"),
        (json.dumps({"event": "other.thing"}), "unsupported_event"),
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


def test_delete_after_commit_and_invalid_left_for_dlq(admin: Engine, engine: Engine) -> None:
    doc = new_doc(admin, "uploaded")
    sqs = FakeSqs([event(doc, "validated"), "garbage", event(uuid4(), "validated")])
    assert consume_once(sqs, "q", make_session_factory(engine)) == 2
    assert sqs.deleted == ["r0", "r2"]  # unknown id is dropped (deleted); garbage is not
    assert status_of(admin, doc) == "validated"
