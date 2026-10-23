from collections.abc import Iterator
from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.extraction.application.service import ReviewService
from medilens.modules.extraction.domain.models import MAX_USER_VALUE_LEN, FieldView
from medilens.modules.extraction.infra.sql_repository import SqlReviewRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["extraction"])

_PROBLEMS = {
    400: {"description": "Validation failed"},
    401: {"description": "Unauthenticated"},
    404: {"description": "Not found"},
    422: {"description": "Low-confidence fields still unconfirmed (body has field_ids)"},
}


class FieldOut(BaseModel):
    id: UUID
    field_path: str
    value: str | None
    user_value: str | None
    confidence: float | None
    source_page: int | None
    source_box: Any
    needs_confirmation: bool
    confirmed_at: datetime | None

    @classmethod
    def of(cls, f: FieldView) -> "FieldOut":
        return cls(**f.__dict__, needs_confirmation=f.needs_confirmation)


class EditRequest(BaseModel):
    user_value: str = Field(min_length=1, max_length=MAX_USER_VALUE_LEN)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:  # uncommitted work is rolled back on close
        yield session


def get_service(session: Annotated[Session, Depends(get_session)]) -> ReviewService:
    return ReviewService(SqlReviewRepository(session))


@router.get("/documents/{document_id}/fields", response_model=list[FieldOut], responses=_PROBLEMS)
def list_fields(
    document_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[ReviewService, Depends(get_service)],
) -> list[FieldOut]:
    return [FieldOut.of(f) for f in service.list_fields(user.sub, document_id)]


@router.patch(
    "/documents/{document_id}/fields/{field_id}", response_model=FieldOut, responses=_PROBLEMS
)
def edit_field(
    document_id: UUID,
    field_id: UUID,
    body: EditRequest,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[ReviewService, Depends(get_service)],
    session: Annotated[Session, Depends(get_session)],
) -> FieldOut:
    out = FieldOut.of(service.edit_field(user.sub, document_id, field_id, body.user_value))
    session.commit()
    return out


@router.post("/documents/{document_id}/confirm", status_code=204, responses=_PROBLEMS)
def confirm(
    document_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[ReviewService, Depends(get_service)],
    session: Annotated[Session, Depends(get_session)],
) -> None:
    service.confirm(user.sub, document_id)
    session.commit()
