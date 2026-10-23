"""SEC-AZ-05: admin has no PHI access; break-glass needs a reason, lasts 1 h, alerts, is audited."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.modules.admin.api import router as admin_router
from medilens.modules.admin.domain.models import Grant
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import event, text

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401

REASON = "Synthetic incident INC-1 needs review"


class RecordingAlerts:
    def __init__(self) -> None:
        self.opened: list[Grant] = []

    def break_glass_opened(self, grant: Grant) -> None:
        self.opened.append(grant)


@dataclass
class Env:
    url: str
    alerts: RecordingAlerts
    current: dict[str, Principal]
    client: TestClient
    anon: TestClient
    profile: UUID  # alice's
    other_profile: UUID  # bob's
    docs: list[UUID] = field(default_factory=list)  # alice's documents

    def sql(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        engine = make_engine(self.url)
        try:
            with engine.begin() as c:
                r = c.execute(text(sql), params)
                return [tuple(x) for x in r] if r.returns_rows else []
        finally:
            engine.dispose()

    def open_grant(self, **over: object) -> str:
        body = {"profile_id": str(self.profile), "reason": REASON, **over}
        r = self.client.post("/v1/admin/break-glass", json=body)
        assert r.status_code == 201, r.text
        return r.json()["id"]


ADMIN = Principal(sub="root-admin", roles=frozenset({"medilens-admin"}))


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    profiles: list[UUID] = []
    docs: list[UUID] = []
    with engine.begin() as c:
        for sub in ("alice", "bob"):
            uid = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            profiles.append(
                c.execute(
                    text(
                        "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (:u) "
                        "RETURNING id"
                    ),
                    {"u": uid},
                ).scalar_one()
            )
        for p, status in (
            (profiles[0], "confirmed"),
            (profiles[0], "uploaded"),
            (profiles[1], "x"),
        ):
            d = c.execute(
                text(
                    "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime, status)"
                    " VALUES (:p, 'k', :h, 'application/pdf', :s) RETURNING id"
                ),
                {"p": p, "h": status, "s": status},
            ).scalar_one()
            if p == profiles[0]:
                docs.append(d)

    @event.listens_for(engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(engine)
    alerts = RecordingAlerts()
    current = {"p": ADMIN}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(admin_router.router, prefix="/v1")
        app.dependency_overrides[admin_router.get_session_factory] = lambda: factory
        app.dependency_overrides[admin_router.get_alert_sink] = lambda: alerts
        app.dependency_overrides[get_token_validator] = lambda: None
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: current["p"]
        return TestClient(app)

    yield Env(
        migrated_url, alerts, current, make_client(True), make_client(False),
        profiles[0], profiles[1], docs,
    )  # fmt: skip
    engine.dispose()


OPS = [
    ("GET", "/v1/admin/stats", None),
    ("POST", "/v1/admin/break-glass", {"profile_id": "00000000-0000-0000-0000-000000000001", "reason": REASON}),
    ("GET", "/v1/admin/break-glass/00000000-0000-0000-0000-000000000001/documents", None),
]  # fmt: skip


@pytest.mark.parametrize("method,path,body", OPS)
def test_authz_matrix(env: Env, method: str, path: str, body: dict | None) -> None:
    assert env.anon.request(method, path, json=body).status_code == 401
    for p in (Principal(sub="alice"), Principal(sub="x", roles=frozenset({"patient"}))):
        env.current["p"] = p
        r = env.client.request(method, path, json=body)
        assert r.status_code == 403
        assert r.headers["content-type"].startswith("application/problem+json")


def test_stats_has_counts_only(env: Env) -> None:
    r = env.client.get("/v1/admin/stats")
    assert r.status_code == 200
    assert r.json() == {
        "counts": {"users": 2, "documents.confirmed": 1, "documents.uploaded": 1, "documents.x": 1}
    }


def test_admin_cannot_read_documents_without_grant(env: Env) -> None:
    unknown = "00000000-0000-0000-0000-000000000009"
    assert env.client.get(f"/v1/admin/break-glass/{unknown}/documents").status_code == 403


@pytest.mark.parametrize("reason", ["", "short", "         x         "])
def test_reason_required(env: Env, reason: str) -> None:
    r = env.client.post(
        "/v1/admin/break-glass", json={"profile_id": str(env.profile), "reason": reason}
    )
    assert r.status_code == 400
    assert env.alerts.opened == []


def test_unknown_profile_404(env: Env) -> None:
    r = env.client.post(
        "/v1/admin/break-glass",
        json={"profile_id": "00000000-0000-0000-0000-000000000009", "reason": REASON},
    )
    assert r.status_code == 404


def test_open_grant_one_hour_alert_and_audit(env: Env) -> None:
    before = datetime.now(timezone.utc)
    gid = env.open_grant(ticket="INC-1")
    ((expires, created),) = env.sql(
        "SELECT expires_at, created_at FROM audit.break_glass_grants WHERE id = :g", g=gid
    )
    assert timedelta(minutes=59) < expires - before < timedelta(minutes=61)
    assert [str(g.id) for g in env.alerts.opened] == [gid]
    audit = env.sql("SELECT action, resource_type, resource_id FROM audit.audit_events")
    assert audit == [("break_glass.opened", "break_glass_grant", UUID(gid))]


def test_alert_failure_rolls_grant_back(env: Env) -> None:
    def boom(grant: Grant) -> None:
        raise RuntimeError("pager down")

    env.alerts.break_glass_opened = boom  # type: ignore[method-assign]
    client = TestClient(env.client.app, raise_server_exceptions=False)
    r = client.post(
        "/v1/admin/break-glass", json={"profile_id": str(env.profile), "reason": REASON}
    )
    assert r.status_code == 500
    assert env.sql("SELECT count(*) FROM audit.break_glass_grants") == [(0,)]


def test_active_grant_lists_only_granted_profile_and_audits(env: Env) -> None:
    gid = env.open_grant()
    r = env.client.get(f"/v1/admin/break-glass/{gid}/documents")
    assert r.status_code == 200
    assert {d["id"] for d in r.json()} == {str(d) for d in env.docs}
    assert all(set(d) == {"id", "status"} for d in r.json())
    actions = [a for (a,) in env.sql("SELECT action FROM audit.audit_events ORDER BY at, id")]
    assert actions == ["break_glass.opened", "break_glass.read_documents"]


def test_grant_is_bound_to_its_admin(env: Env) -> None:
    gid = env.open_grant()
    env.current["p"] = Principal(sub="other-admin", roles=frozenset({"medilens-admin"}))
    assert env.client.get(f"/v1/admin/break-glass/{gid}/documents").status_code == 403


def test_expired_and_revoked_grants_403(env: Env) -> None:
    expired, revoked = env.open_grant(), env.open_grant()
    env.sql(
        "UPDATE audit.break_glass_grants SET expires_at = now() - interval '1 second' WHERE id = :g",
        g=expired,
    )
    env.sql("UPDATE audit.break_glass_grants SET revoked_at = now() WHERE id = :g", g=revoked)
    for gid in (expired, revoked):
        assert env.client.get(f"/v1/admin/break-glass/{gid}/documents").status_code == 403


def test_db_function_rechecks_expiry_itself(env: Env) -> None:
    """Even if the app check were skipped, the definer function returns nothing for a dead grant."""
    gid = env.open_grant()
    env.sql(
        "UPDATE audit.break_glass_grants SET expires_at = now() - interval '1 second' WHERE id = :g",
        g=gid,
    )
    assert env.sql("SELECT * FROM audit.break_glass_documents(:g, 'root-admin')", g=gid) == []


def test_app_role_cannot_bypass_rls_or_extend_grant(env: Env) -> None:
    """app_rw (the API login) still sees no clinical rows without app.profile_ids, and can't UPDATE."""
    engine = make_engine(env.url)
    try:
        with engine.begin() as c:
            c.exec_driver_sql("SET LOCAL ROLE app_rw")
            assert c.execute(text("SELECT count(*) FROM clinical.documents")).scalar_one() == 0
        gid = env.open_grant()
        with engine.connect() as c:
            c.exec_driver_sql("SET ROLE app_rw")
            with pytest.raises(Exception, match="permission denied"):
                c.execute(
                    text(
                        "UPDATE audit.break_glass_grants SET expires_at = now() + interval '9 d' WHERE id = :g"
                    ),
                    {"g": gid},
                )
    finally:
        engine.dispose()
