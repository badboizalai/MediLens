from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.modules.extraction.api import router as ex_router
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import event, text

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401


@dataclass
class Env:
    client: TestClient
    anon: TestClient  # real auth dependency: no override
    url: str
    current: dict[str, str]
    doc: UUID  # alice's document
    low: UUID  # alice's low-confidence field
    high: UUID  # alice's high-confidence field

    def query(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        engine = make_engine(self.url)
        try:
            with engine.connect() as c:
                return [tuple(r) for r in c.execute(text(sql), params)]
        finally:
            engine.dispose()


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    with engine.begin() as c:
        profile = None
        for sub in ("alice", "bob"):
            uid = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            p = c.execute(
                text(
                    "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) RETURNING id"
                ),
                {"u": uid},
            ).scalar_one()
            profile = profile or p  # alice's
        doc = c.execute(
            text(
                "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime) "
                "VALUES (:p, 'k', 'h', 'application/pdf') RETURNING id"
            ),
            {"p": profile},
        ).scalar_one()
        run = c.execute(
            text(
                "INSERT INTO clinical.extraction_runs (profile_id, document_id, status) "
                "VALUES (:p, :d, 'needs_review') RETURNING id"
            ),
            {"p": profile, "d": doc},
        ).scalar_one()
        ids = [
            c.execute(
                text(
                    "INSERT INTO clinical.extraction_fields "
                    "(profile_id, run_id, field_path, value, confidence, source_page) "
                    "VALUES (:p, :r, :f, 'synthetic', :c, 1) RETURNING id"
                ),
                {"p": profile, "r": run, "f": f, "c": conf},
            ).scalar_one()
            for f, conf in (("a.low", 0.5), ("b.high", 0.95))
        ]

    @event.listens_for(engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(engine)
    current = {"sub": "alice"}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(ex_router.router, prefix="/v1")
        app.dependency_overrides[ex_router.get_session_factory] = lambda: factory
        app.dependency_overrides[get_token_validator] = lambda: None  # unreached without a token
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
        return TestClient(app)

    yield Env(make_client(True), make_client(False), migrated_url, current, doc, ids[0], ids[1])
    engine.dispose()
