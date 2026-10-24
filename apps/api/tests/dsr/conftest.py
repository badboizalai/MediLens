from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.main import dsr_stores
from medilens.modules.document.api import router as doc_router
from medilens.modules.identity.api import router as id_router
from medilens.modules.identity.domain.dsr import ProfileStore
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import Engine, event, text

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401

EMBEDDING = "[" + ",".join(["0"] * 256) + "]"


class FakeStorage:
    """In-memory stand-in for both buckets (DsrStorage)."""

    def __init__(self) -> None:
        self.keys: set[str] = set()

    def presign_original(self, profile_id: UUID, document_id: UUID, expires_in: int) -> str | None:
        key = f"raw/{document_id}/0000"
        return f"https://s3.test/{key}?exp={expires_in}" if key in self.keys else None

    def list_prefix(self, prefix: str) -> list[str]:
        return sorted(k for k in self.keys if k.startswith(prefix))

    def delete_prefix(self, prefix: str) -> None:
        self.keys -= set(self.list_prefix(prefix))


@dataclass
class Env:
    client: TestClient
    anon: TestClient
    engine: Engine
    current: dict[str, str]
    storage: FakeStorage
    stores: dict[str, Sequence[ProfileStore] | None]  # override to drop a store
    ids: dict[str, UUID] = field(default_factory=dict)  # "alice", "alice_profile", ...

    def query(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        with self.engine.connect() as c:
            return [tuple(r) for r in c.execute(text(sql), params)]


def seed(c, storage: FakeStorage, sub: str, other: UUID | None) -> dict[str, UUID]:  # type: ignore[no-untyped-def]
    """One user with a full footprint in every store. Synthetic values only."""

    def one(sql: str, **p: object) -> UUID:
        return c.execute(text(sql + " RETURNING id"), p).scalar_one()

    u = one("INSERT INTO identity.users (external_sub) VALUES (:s)", s=sub)
    p = one(
        "INSERT INTO identity.patient_profiles (owner_user_id, birth_year) VALUES (:u, 1980)", u=u
    )
    gone = one(  # soft-deleted profile must be erased too
        "INSERT INTO identity.patient_profiles (owner_user_id, deleted_at) VALUES (:u, now())", u=u
    )
    for t in ("health_data_processing", "research_use"):
        c.execute(
            text(
                "INSERT INTO identity.consents (user_id, type, terms_version, given_at) "
                "VALUES (:u, :t, 'v1', now())"
            ),
            {"u": u, "t": t},
        )
    doc = one(
        "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime) "
        "VALUES (:p, :k, :h, 'application/pdf')",
        p=p,
        k=f"quarantine/{p}/x",
        h=f"sha-{sub}",
    )
    c.execute(
        text(
            "INSERT INTO clinical.document_pages (profile_id, document_id, page_no) VALUES (:p, :d, 1)"
        ),
        {"p": p, "d": doc},
    )
    run = one(
        "INSERT INTO clinical.extraction_runs (profile_id, document_id) VALUES (:p, :d)", p=p, d=doc
    )
    c.execute(
        text(
            "INSERT INTO clinical.extraction_fields (profile_id, run_id, field_path, value, "
            "confirmed_at) VALUES (:p, :r, 'dx', 'synthetic', now())"
        ),
        {"p": p, "r": run},
    )
    enc = one(
        "INSERT INTO clinical.encounters (profile_id, facility) VALUES (:p, 'Synthetic Clinic')",
        p=p,
    )
    cond = one(
        "INSERT INTO clinical.conditions (profile_id, encounter_id, label, source) "
        "VALUES (:p, :e, 'synthetic', 'patient_reported')",
        p=p,
        e=enc,
    )
    c.execute(
        text(
            "INSERT INTO clinical.body_findings (profile_id, condition_id, region_code) VALUES (:p, :c, 'liver')"
        ),
        {"p": p, "c": cond},
    )
    c.execute(
        text("INSERT INTO clinical.observations (profile_id, name) VALUES (:p, 'synthetic')"),
        {"p": p},
    )
    c.execute(
        text(
            "INSERT INTO clinical.knowledge_chunks (profile_id, content, embedding) "
            "VALUES (:p, 'synthetic text', CAST(:e AS vector))"
        ),
        {"p": p, "e": EMBEDDING},
    )
    if other:  # a share I gave, and one I received
        c.execute(
            text(
                "INSERT INTO clinical.share_grants (profile_id, grantee_user_id, scope, expires_at) "
                "VALUES (:p, :g, 'findings:read', now() + interval '1 day')"
            ),
            {"p": p, "g": other},
        )
    c.execute(
        text(
            "INSERT INTO audit.audit_events (actor_id, action) VALUES (:u, 'share.create'), (:u, 'x')"
        ),
        {"u": u},
    )
    c.execute(
        text(
            "INSERT INTO audit.break_glass_grants (admin_sub, profile_id, reason, expires_at) "
            "VALUES ('admin', :p, 'synthetic support ticket', now() + interval '1 hour')"
        ),
        {"p": p},
    )
    c.execute(
        text(
            "INSERT INTO clinical.outbox (event_type, payload) VALUES ('document.uploaded', CAST(:j AS jsonb))"
        ),
        {"j": f'{{"profile_id": "{p}", "document_id": "{doc}"}}'},
    )
    c.execute(
        text("INSERT INTO worker.document_status (document_id, status) VALUES (:d, 'ocr_done')"),
        {"d": str(doc)},
    )
    storage.keys |= {
        f"quarantine/{p}/{doc}",
        f"raw/{doc}/0000",
        f"pre/{doc}/0001.png",
        f"ocr/{doc}/0001.json",
        f"extractions/{doc}/{run}.json",
        f"retake/{doc}.json",
    }
    return {sub: u, f"{sub}_profile": p, f"{sub}_gone": gone, f"{sub}_doc": doc}


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    storage = FakeStorage()
    ids: dict[str, UUID] = {}
    with engine.begin() as c:
        ids |= seed(c, storage, "bob", None)
        ids |= seed(c, storage, "alice", ids["bob"])
        # alice is also a grantee of bob's profile
        c.execute(
            text(
                "INSERT INTO clinical.share_grants (profile_id, grantee_user_id, scope, expires_at) "
                "VALUES (:p, :g, 'findings:read', now() + interval '1 day')"
            ),
            {"p": ids["bob_profile"], "g": ids["alice"]},
        )
        c.execute(text("INSERT INTO identity.users (external_sub) VALUES ('carol')"))
    app_engine = make_engine(migrated_url)

    @event.listens_for(app_engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(app_engine)
    current = {"sub": "alice"}
    stores: dict[str, Sequence[ProfileStore] | None] = {"override": None}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(id_router.router, prefix="/v1")
        app.dependency_overrides[id_router.get_session_factory] = lambda: factory
        app.dependency_overrides[doc_router.get_dsr_storage] = lambda: storage
        app.dependency_overrides[id_router.get_dsr_stores] = dsr_stores
        app.dependency_overrides[get_token_validator] = lambda: None
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
        return TestClient(app)

    yield Env(make_client(True), make_client(False), engine, current, storage, stores, ids)
    app_engine.dispose()
    engine.dispose()
