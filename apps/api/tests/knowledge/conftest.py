from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.modules.knowledge.api import router as kn_router
from medilens.modules.knowledge.application.service import KnowledgeService
from medilens.modules.knowledge.infra.hashing_embedder import HashingEmbedder
from medilens.modules.knowledge.infra.sql_repository import SqlKnowledgeRepository
from medilens.shared.auth import Principal, get_current_user, get_token_validator
from sqlalchemy import Engine, event, text
from sqlalchemy.orm import Session

from tests.db.conftest import alembic_cfg, migrated_url, pg_url  # noqa: F401

ARTICLES = Path(__file__).resolve().parents[4] / "content" / "articles"


@dataclass
class Env:
    client: TestClient
    anon: TestClient
    engine: Engine
    current: dict[str, str]
    alice: UUID
    bob: UUID
    drafts: dict[str, bool]

    def index(self, profile: UUID, body: str, ref: str) -> None:
        with Session(self.engine) as s, s.begin():
            KnowledgeService(SqlKnowledgeRepository(s), HashingEmbedder()).index_profile_text(
                profile, body, ref
            )

    def ingest(self, raw: str) -> None:
        with Session(self.engine) as s, s.begin():  # superuser: may write public chunks
            KnowledgeService(SqlKnowledgeRepository(s), HashingEmbedder()).ingest_article(raw)

    def count(self) -> int:
        with self.engine.connect() as c:
            return c.execute(text("SELECT count(*) FROM clinical.knowledge_chunks")).scalar_one()

    def search(self, profile: UUID, query: str, k: int = 10) -> list[dict[str, Any]]:
        r = self.client.post(
            f"/v1/profiles/{profile}/knowledge/search", json={"query": query, "k": k}
        )
        assert r.status_code == 200, r.text
        return r.json()["chunks"]  # type: ignore[no-any-return]


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
    app_engine = make_engine(migrated_url)

    @event.listens_for(app_engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(app_engine)
    current = {"sub": "alice"}
    drafts = {"allow": True}

    def make_client(authenticated: bool) -> TestClient:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(RequestValidationError, validation_error_handler)
        app.include_router(kn_router.router, prefix="/v1")
        app.dependency_overrides[kn_router.get_session_factory] = lambda: factory
        app.dependency_overrides[kn_router.get_allow_drafts] = lambda: drafts["allow"]
        app.dependency_overrides[get_token_validator] = lambda: None
        if authenticated:
            app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
        return TestClient(app)

    yield Env(make_client(True), make_client(False), engine, current, *profiles, drafts)
    app_engine.dispose()
    engine.dispose()
