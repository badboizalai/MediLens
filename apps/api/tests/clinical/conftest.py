import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.main import clinical_confirm_hook
from medilens.modules.clinical.api import router as cl_router
from medilens.modules.extraction.api import router as ex_router
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import Engine, event, text

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401


def leaf(value: Any, page: int = 1) -> dict[str, Any]:
    return {"value": value, "confidence": 0.95, "source": {"page": page, "quote": "q"}}


ONCOLOGY: dict[str, Any] = {
    "encounter": {"date": leaf("2026-03-01"), "facility": leaf("Synthetic Clinic")},
    "primary": {
        "site": leaf("synthetic site"),
        "histology": leaf("synthetic carcinoma"),
        "laterality": "left",
        "size_mm": leaf(22.5),
        "region": {"region_code": "lung_left_upper", "confidence": 0.9},
    },
    "tnm": {"stage": leaf("II")},
    "metastases": [
        {
            "site": leaf("liver"),
            "stated_as": "confirmed",
            "region": {"region_code": "liver", "confidence": 0.9},
        },
        {
            "site": leaf("bone"),
            "stated_as": "suspected",
            "region": {"region_code": None, "confidence": 0.2},
        },
    ],
}
CARDIOLOGY: dict[str, Any] = {
    "encounter": {"date": leaf("2026-04-02")},
    "diagnoses": [
        {
            "text": leaf("synthetic finding"),
            "severity": "mild",
            "region": {"region_code": "heart_lv", "confidence": 0.8},
        }
    ],
    "observations": [
        {
            "name": leaf("LVEF"),
            "value": {**leaf(55), "unit": "%"},
            "reference_range": leaf("50-70"),
            "loinc_hint": "10230-1",
        }
    ],
}


@dataclass
class Env:
    client: TestClient
    anon: TestClient
    engine: Engine
    current: dict[str, str]
    alice_profile: UUID
    doc: UUID

    def query(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        with self.engine.connect() as c:
            return [tuple(r) for r in c.execute(text(sql), params)]

    def run(self, raw: dict[str, Any], paths: dict[str, str] | None = None) -> UUID:
        """An extraction run awaiting confirmation; `paths` become extraction_fields rows."""
        with self.engine.begin() as c:
            run = c.execute(
                text(
                    "INSERT INTO clinical.extraction_runs "
                    "(profile_id, document_id, status, raw_output) "
                    "VALUES (:p, :d, 'needs_review', CAST(:raw AS jsonb)) RETURNING id"
                ),
                {"p": self.alice_profile, "d": self.doc, "raw": json.dumps(raw)},
            ).scalar_one()
            for path, value in (paths or {}).items():
                c.execute(
                    text(
                        "INSERT INTO clinical.extraction_fields "
                        "(profile_id, run_id, field_path, value, confidence) "
                        "VALUES (:p, :r, :f, :v, 0.95)"
                    ),
                    {"p": self.alice_profile, "r": run, "f": path, "v": value},
                )
        return run

    def confirm(self) -> int:
        return self.client.post(f"/v1/documents/{self.doc}/confirm").status_code


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    with engine.begin() as c:
        profiles = []
        for sub in ("alice", "bob"):
            uid = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            profiles.append(
                c.execute(
                    text(
                        "INSERT INTO identity.patient_profiles (owner_user_id) "
                        "VALUES (:u) RETURNING id"
                    ),
                    {"u": uid},
                ).scalar_one()
            )
        doc = c.execute(
            text(
                "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime) "
                "VALUES (:p, 'k', 'h', 'application/pdf') RETURNING id"
            ),
            {"p": profiles[0]},
        ).scalar_one()

    app_engine = make_engine(migrated_url)

    @event.listens_for(app_engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(app_engine)
    current = {"sub": "alice"}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(ex_router.router, prefix="/v1")
        app.include_router(cl_router.router, prefix="/v1")
        for mod in (ex_router, cl_router):
            app.dependency_overrides[mod.get_session_factory] = lambda: factory
        app.dependency_overrides[ex_router.get_confirm_hook] = clinical_confirm_hook
        app.dependency_overrides[get_token_validator] = lambda: None
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
        return TestClient(app)

    yield Env(make_client(True), make_client(False), engine, current, profiles[0], doc)
    app_engine.dispose()
    engine.dispose()
