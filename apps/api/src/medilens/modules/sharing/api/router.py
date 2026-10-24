from collections.abc import Callable, Iterator
from datetime import datetime
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.sharing.application.service import MAX_LIMIT, SharingService, utc_now
from medilens.modules.sharing.domain.models import MAX_EXPIRES_HOURS
from medilens.modules.sharing.infra.cedar import CedarShareAuthorizer
from medilens.modules.sharing.infra.sql_repository import SqlShareRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["sharing"])

_PROBLEMS = {
    401: {"description": "Unauthenticated"},
    403: {"description": "Share expired, revoked or out of scope"},
    404: {"description": "Not found"},
}


class ShareCreate(BaseModel):
    grantee_user_id: UUID
    expires_in_hours: int = Field(ge=1, le=MAX_EXPIRES_HOURS)


class ShareOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    profile_id: UUID
    grantee_user_id: UUID
    scope: str
    expires_at: datetime
    revoked_at: datetime | None


class SharedShareOut(BaseModel):
    """Grantee view: no profile or owner identifiers."""

    share_id: UUID
    scope: str
    expires_at: datetime
    status: str = "active"  # denied shares never reach here (403/404)


class SharedFindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    region_code: str
    laterality: str | None
    severity: str | None
    unit_code: str | None
    is_metastasis: bool
    observed_at: datetime | None
    label: str | None


class SharedFindingsPage(BaseModel):
    findings: list[SharedFindingOut]
    next_cursor: UUID | None


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:
        yield session


def get_clock() -> Callable[[], datetime]:
    return utc_now  # tests override this to inject time


def get_service(
    session: Annotated[Session, Depends(get_session)],
    clock: Annotated[Callable[[], datetime], Depends(get_clock)],
) -> SharingService:
    return SharingService(SqlShareRepository(session), CedarShareAuthorizer(), clock)


Service = Annotated[SharingService, Depends(get_service)]
User = Annotated[Principal, Depends(get_current_user)]


@router.post(
    "/profiles/{profile_id}/shares", status_code=201, response_model=ShareOut, responses=_PROBLEMS
)
def create_share(profile_id: UUID, body: ShareCreate, user: User, service: Service) -> ShareOut:
    grant = service.create(user.sub, profile_id, body.grantee_user_id, body.expires_in_hours)
    return ShareOut.model_validate(grant)


@router.get("/profiles/{profile_id}/shares", response_model=list[ShareOut], responses=_PROBLEMS)
def list_shares(profile_id: UUID, user: User, service: Service) -> list[ShareOut]:
    return [ShareOut.model_validate(g) for g in service.list_shares(user.sub, profile_id)]


@router.delete("/shares/{share_id}", status_code=204, responses=_PROBLEMS)
def revoke_share(share_id: UUID, user: User, service: Service) -> Response:
    service.revoke(user.sub, share_id)
    return Response(status_code=204)


@router.get("/shared/{share_id}", response_model=SharedShareOut, responses=_PROBLEMS)
def shared_share(share_id: UUID, user: User, service: Service) -> SharedShareOut:
    g = service.get_share(user.sub, share_id)
    return SharedShareOut(share_id=g.id, scope=g.scope, expires_at=g.expires_at)


@router.get("/shared/{share_id}/findings", response_model=SharedFindingsPage, responses=_PROBLEMS)
def shared_findings(
    share_id: UUID,
    user: User,
    service: Service,
    cursor: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 50,
) -> SharedFindingsPage:
    rows, nxt = service.read_findings(user.sub, share_id, cursor, limit)
    return SharedFindingsPage(
        findings=[SharedFindingOut.model_validate(r) for r in rows], next_cursor=nxt
    )
