from collections.abc import Iterator
from datetime import datetime
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.clinical.application.service import MAX_LIMIT, ClinicalService
from medilens.modules.clinical.infra.sql_repository import SqlClinicalRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["clinical"])

_PROBLEMS = {
    400: {"description": "Validation failed"},
    401: {"description": "Unauthenticated"},
    404: {"description": "Not found"},
}


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    region_code: str
    laterality: str | None
    severity: str | None
    unit_code: str | None
    is_metastasis: bool
    observed_at: datetime | None
    document_id: UUID | None
    label: str | None


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    value: str | None
    unit: str | None
    loinc_code: str | None
    ref_low: float | None
    ref_high: float | None
    observed_at: datetime | None
    document_id: UUID | None


class FindingsPage(BaseModel):
    findings: list[FindingOut]
    observations: list[ObservationOut]  # first page only
    next_cursor: UUID | None


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:
        yield session


def get_service(session: Annotated[Session, Depends(get_session)]) -> ClinicalService:
    return ClinicalService(SqlClinicalRepository(session))


@router.get("/profiles/{profile_id}/findings", response_model=FindingsPage, responses=_PROBLEMS)
def list_findings(
    profile_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[ClinicalService, Depends(get_service)],
    cursor: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 50,
) -> FindingsPage:
    findings, observations, nxt = service.list_findings(user.sub, profile_id, cursor, limit)
    return FindingsPage(
        findings=[FindingOut.model_validate(f) for f in findings],
        observations=[ObservationOut.model_validate(o) for o in observations],
        next_cursor=nxt,
    )
