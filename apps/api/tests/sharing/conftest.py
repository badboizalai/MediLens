from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.modules.sharing.api import router as sh_router
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import Engine, event, text

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401

T0 = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)


@dataclass
class Env:
    client: TestClient
    anon: TestClient
    engine: Engine
    current: dict[str, str]
    clock: dict[str, datetime]
    users: dict[str, UUID]
    profile: UUID  # alice's
    bob_profile: UUID

    def query(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        with self.engine.connect() as c:
            return [tuple(r) for r in c.execute(text(sql), params)]

    def share(self, hours: int = 24, grantee: str = "bob") -> str:
        r = self.client.post(
            f"/v1/profiles/{self.profile}/shares",
            json={"grantee_user_id": str(self.users[grantee]), "expires_in_hours": hours},
        )
        assert r.status_code == 201, r.text
        return str(r.json()["id"])

    def advance(self, **delta: float) -> None:
        self.clock["now"] += timedelta(**delta)


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    users: dict[str, UUID] = {}
    profiles: dict[str, UUID] = {}
    with engine.begin() as c:
        for sub in ("alice", "bob", "carol"):
            users[sub] = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            profiles[sub] = c.execute(
                text(
                    "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) RETURNING id"
                ),
                {"u": users[sub]},
            ).scalar_one()
        for sub, region in (("alice", "liver"), ("bob", "heart_lv")):  # bob's must never leak
            cid = c.execute(
                text(
                    "INSERT INTO clinical.conditions (profile_id, unit_code, label) "
                    "VALUES (:p, 'oncology', 'synthetic') RETURNING id"
                ),
                {"p": profiles[sub]},
            ).scalar_one()
            c.execute(
                text(
                    "INSERT INTO clinical.body_findings (profile_id, condition_id, region_code) "
                    "VALUES (:p, :c, :r)"
                ),
                {"p": profiles[sub], "c": cid, "r": region},
            )

    app_engine = make_engine(migrated_url)

    @event.listens_for(app_engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(app_engine)
    current = {"sub": "alice"}
    clock = {"now": T0}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(sh_router.router, prefix="/v1")
        app.dependency_overrides[sh_router.get_session_factory] = lambda: factory
        app.dependency_overrides[sh_router.get_clock] = lambda: lambda: clock["now"]
        app.dependency_overrides[get_token_validator] = lambda: None
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
        return TestClient(app)

    yield Env(
        make_client(True),
        make_client(False),
        engine,
        current,
        clock,
        users,
        profiles["alice"],
        profiles["bob"],
    )
    app_engine.dispose()
    engine.dispose()
