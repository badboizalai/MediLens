import os
from collections.abc import Iterator
from datetime import datetime
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, StringConstraints
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.core.errors import Forbidden
from medilens.modules.admin.application.service import AdminService
from medilens.modules.admin.domain.models import MIN_REASON_LEN
from medilens.modules.admin.infra.alerts import LogAlertSink
from medilens.modules.admin.infra.sql_repository import SqlAdminRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

_PROBLEMS = {
    401: {"description": "Unauthenticated"},
    403: {"description": "Not an admin, or no active break-glass grant"},
}


def admin_role() -> str:
    return os.environ.get("MEDILENS_ADMIN_ROLE", "medilens-admin")  # IdP group/role claim value


def require_admin(user: Annotated[Principal, Depends(get_current_user)]) -> Principal:
    if not user.has_role(admin_role()):
        raise Forbidden("Admin role required")
    return user


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:  # uncommitted work is rolled back on close
        yield session


def get_alert_sink() -> LogAlertSink:
    return LogAlertSink()


def get_service(
    session: Annotated[Session, Depends(get_session)],
    alerts: Annotated[LogAlertSink, Depends(get_alert_sink)],
) -> AdminService:
    return AdminService(SqlAdminRepository(session), alerts)


Admin = Annotated[Principal, Depends(require_admin)]
Service = Annotated[AdminService, Depends(get_service)]


class StatsOut(BaseModel):
    counts: dict[str, int]


class BreakGlassRequest(BaseModel):
    profile_id: UUID
    reason: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=MIN_REASON_LEN, max_length=500)
    ]
    ticket: str | None = Field(default=None, max_length=64)


class GrantOut(BaseModel):
    id: UUID
    profile_id: UUID
    expires_at: datetime


class DocumentMetaOut(BaseModel):
    id: UUID
    status: str


@router.get("/stats", response_model=StatsOut, responses=_PROBLEMS)
def stats(_: Admin, service: Service) -> StatsOut:
    return StatsOut(counts=service.stats())


@router.post("/break-glass", status_code=201, response_model=GrantOut, responses=_PROBLEMS)
def open_break_glass(
    body: BreakGlassRequest,
    admin: Admin,
    service: Service,
    session: Annotated[Session, Depends(get_session)],
) -> GrantOut:
    g = service.open_break_glass(admin.sub, body.profile_id, body.reason, body.ticket)
    session.commit()
    return GrantOut(id=g.id, profile_id=g.profile_id, expires_at=g.expires_at)


@router.get(
    "/break-glass/{grant_id}/documents", response_model=list[DocumentMetaOut], responses=_PROBLEMS
)
def grant_documents(
    grant_id: UUID,
    admin: Admin,
    service: Service,
    session: Annotated[Session, Depends(get_session)],
) -> list[DocumentMetaOut]:
    docs = service.list_documents(admin.sub, grant_id)
    session.commit()  # persists the access audit row
    return [DocumentMetaOut(id=d.id, status=d.status) for d in docs]
