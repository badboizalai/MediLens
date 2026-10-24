import json
from collections.abc import Iterator
from uuid import uuid4

import pytest
from medilens.core.db import make_engine, make_session_factory
from medilens.modules.extraction.infra.ingest import result_key
from medilens.shared.api_events_consumer import InvalidEvent, handle
from sqlalchemy import Engine, text
from sqlalchemy import event as sa_event
from sqlalchemy.exc import ProgrammingError

from tests.db.conftest import (  # noqa: F401  (Testcontainers fixtures)
    alembic_cfg,
    migrated_url,
    pg_url,
)
from tests.shared.test_api_events_consumer import new_doc


class FakeReader:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def read(self, key: str) -> bytes:
        return self.objects[key]


def completed(doc: object, run: object) -> str:
    return json.dumps(
        {
            "schemaVersion": 1,
            "event": "extraction.completed",
            "documentId": str(doc),
            "runId": str(run),
        }
    )


def cited(value: str, page: int, **src: object) -> dict[str, object]:
    return {"value": value, "confidence": 0.9, "source": {"page": page, "quote": value, **src}}


def result(doc: object, run: object, **over: object) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "documentId": str(doc),
        "runId": str(run),
        "unit": "dental",
        "model": "synthetic-model",
        "promptVersion": "v1",
        "costUsd": 0.001,
        "confidence": 0.9,
        "repaired": False,
        "flags": [],
        "result": {
            "encounter": {"facility": cited("Clinic A", 1)},
            "teeth": [{"fdi": cited("16", 2, bbox=[0.1, 0.2, 0.3, 0.4]), "condition": "caries"}],
        },
        **over,
    }


@pytest.fixture
def admin(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    eng = make_engine(migrated_url)
    yield eng
    eng.dispose()


@pytest.fixture
def engine(migrated_url: str) -> Iterator[Engine]:  # noqa: F811
    eng = make_engine(migrated_url)

    @sa_event.listens_for(eng, "begin")
    def _as_consumer(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE api_events_consumer")

    yield eng
    eng.dispose()


def put(reader: FakeReader, doc: object, run: object, obj: dict[str, object]) -> None:
    reader.objects[result_key(doc, run)] = json.dumps(obj).encode()  # type: ignore[arg-type]


def test_ingest_happy_path_and_idempotent(admin: Engine, engine: Engine) -> None:
    doc, run, reader = new_doc(admin, "extracted"), uuid4(), FakeReader()
    put(reader, doc, run, result(doc, run))
    sf = make_session_factory(engine)
    assert handle(completed(doc, run), sf, reader) == "ingested"
    assert handle(completed(doc, run), sf, reader) == "duplicate"  # redelivery
    with admin.connect() as c:
        r = c.execute(
            text(
                "SELECT profile_id, document_id, model, status "
                "FROM clinical.extraction_runs WHERE id=:r"
            ),
            {"r": str(run)},
        ).one()
        prof = c.execute(
            text("SELECT profile_id FROM clinical.documents WHERE id=:d"), {"d": doc}
        ).scalar_one()
        fields = c.execute(
            text(
                "SELECT field_path, value, confidence, source_page, source_box, profile_id "
                "FROM clinical.extraction_fields WHERE run_id=:r ORDER BY field_path"
            ),
            {"r": str(run)},
        ).all()
    assert r.profile_id == prof
    assert (str(r.document_id), r.model, r.status) == (doc, "synthetic-model", "completed")
    assert [(f.field_path, f.value, f.source_page) for f in fields] == [
        ("encounter.facility", "Clinic A", 1),
        ("teeth[0].fdi", "16", 2),
    ]
    assert fields[1].source_box == [0.1, 0.2, 0.3, 0.4]
    assert fields[0].source_box is None
    assert all(f.profile_id == prof for f in fields)


def test_unknown_document_goes_to_dlq_path(engine: Engine) -> None:
    ghost, run, reader = uuid4(), uuid4(), FakeReader()
    put(reader, ghost, run, result(ghost, run))
    with pytest.raises(InvalidEvent) as e:
        handle(completed(ghost, run), make_session_factory(engine), reader)
    assert e.value.reason == "unknown_document"


def test_consumer_cannot_touch_clinical_tables_directly(engine: Engine) -> None:
    for sql in (
        "INSERT INTO clinical.extraction_runs (profile_id, document_id) "
        "VALUES (gen_random_uuid(), gen_random_uuid())",
        "INSERT INTO clinical.extraction_fields (profile_id, run_id, field_path) "
        "VALUES (gen_random_uuid(), gen_random_uuid(), 'x')",
        "SELECT 1 FROM clinical.extraction_runs",
    ):
        with pytest.raises(ProgrammingError, match="permission denied"), engine.begin() as c:
            c.execute(text(sql))


def test_function_is_not_executable_by_app_rw(admin: Engine) -> None:
    with pytest.raises(ProgrammingError, match="permission denied"), admin.begin() as c:
        c.exec_driver_sql("SET LOCAL ROLE app_rw")
        c.execute(
            text(
                "SELECT clinical.ingest_extraction(gen_random_uuid(), gen_random_uuid(), "
                "null, 'm', 'p', 0, 0, '{}', '[]')"
            )
        )


def test_malformed_payloads_rejected(admin: Engine, engine: Engine) -> None:
    doc, run, reader = new_doc(admin, "extracted"), uuid4(), FakeReader()
    sf = make_session_factory(engine)
    msg = json.loads(completed(doc, run))
    for bad in ({"event": "extraction.completed"}, {**msg, "profileId": str(uuid4())}):
        with pytest.raises(InvalidEvent) as e:
            handle(json.dumps(bad), sf, reader)
        assert e.value.reason == "schema_violation"  # a profile id is never accepted
    for obj, reason in (
        (result(doc, run, confidence=7), "result_schema_violation"),
        (result(doc, run, extra="x"), "result_schema_violation"),
        (result(doc, run, unit="ophthalmology"), "result_schema_violation"),
        (result(doc, uuid4()), "result_id_mismatch"),
    ):
        put(reader, doc, run, obj)
        with pytest.raises(InvalidEvent) as e:
            handle(completed(doc, run), sf, reader)
        assert e.value.reason == reason
    with admin.connect() as c:
        assert c.execute(text("SELECT count(*) FROM clinical.extraction_runs")).scalar_one() == 0
