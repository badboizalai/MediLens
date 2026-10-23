import hashlib
from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import AppError, app_error_handler, validation_error_handler
from medilens.modules.document.api import router as doc_router
from medilens.modules.document.domain.models import Presigned
from medilens.shared.auth import Principal, get_current_user
from sqlalchemy import event, text

from tests.db.conftest import (  # noqa: F401  (Testcontainers fixtures)
    alembic_cfg,
    migrated_url,
    pg_url,
)


class FakeStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.sizes: dict[str, int] = {}  # override reported size without allocating bytes
        self.presigned: list[dict[str, object]] = []

    def presign_put(
        self, key: str, content_type: str, size_bytes: int, expires_in: int
    ) -> Presigned:
        self.presigned.append({"key": key, "type": content_type, "size": size_bytes})
        return Presigned(
            f"https://storage.test/{key}?sig=x", {"Content-Type": content_type}, expires_in
        )

    def put(self, key: str, data: bytes) -> None:
        self.objects[key] = data

    def size(self, key: str) -> int | None:
        if key not in self.objects:
            return None
        return self.sizes.get(key, len(self.objects[key]))

    def read_head(self, key: str, n: int) -> bytes:
        return self.objects[key][:n]

    def sha256(self, key: str) -> str:
        return hashlib.sha256(self.objects[key]).hexdigest()

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)


@dataclass
class Env:
    client: TestClient
    storage: FakeStorage
    url: str
    current: dict[str, str]
    alice_profile: UUID
    bob_profile: UUID

    def as_user(self, sub: str) -> None:
        self.current["sub"] = sub

    def query(self, sql: str, **params: object) -> list[tuple[object, ...]]:
        engine = make_engine(self.url)
        try:
            with engine.connect() as c:
                return [tuple(r) for r in c.execute(text(sql), params)]
        finally:
            engine.dispose()


PNG = b"\x89PNG\r\n\x1a\n" + b"synthetic-bytes"
PDF = b"%PDF-1.7\n%synthetic"


@pytest.fixture
def env(migrated_url: str) -> Iterator[Env]:  # noqa: F811
    engine = make_engine(migrated_url)
    with engine.begin() as c:
        ids: list[UUID] = []
        for sub in ("alice", "bob"):
            uid = c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s) RETURNING id"),
                {"s": sub},
            ).scalar_one()
            ids.append(
                c.execute(
                    text(
                        "INSERT INTO identity.patient_profiles (owner_user_id) "
                        "VALUES (:u) RETURNING id"
                    ),
                    {"u": uid},
                ).scalar_one()
            )

    @event.listens_for(engine, "begin")
    def _as_app_rw(conn):  # type: ignore[no-untyped-def]
        conn.exec_driver_sql("SET LOCAL ROLE app_rw")  # RLS applies, like the real login role

    factory = make_session_factory(engine)
    storage = FakeStorage()
    current = {"sub": "alice"}
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.include_router(doc_router.router, prefix="/v1")
    app.dependency_overrides[doc_router.get_session_factory] = lambda: factory
    app.dependency_overrides[doc_router.get_storage] = lambda: storage
    app.dependency_overrides[get_current_user] = lambda: Principal(sub=current["sub"])
    yield Env(TestClient(app), storage, migrated_url, current, ids[0], ids[1])
    engine.dispose()
