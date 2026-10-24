from collections.abc import Iterator, Sequence
from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.identity.application.dsr_service import DsrService
from medilens.modules.identity.domain.dsr import CONFIRM_PHRASE, ProfileStore
from medilens.modules.identity.infra.dsr_repository import SqlDsrRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["identity"])

_PROBLEMS = {
    400: {"description": "Validation failed"},
    401: {"description": "Unauthenticated"},
    404: {"description": "Not found"},
}


class MeOut(BaseModel):
    sub: str
    roles: list[str]


@router.get("/me", response_model=MeOut)
def me(user: Annotated[Principal, Depends(get_current_user)]) -> MeOut:
    return MeOut(sub=user.sub, roles=sorted(user.roles))


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:  # uncommitted work is rolled back on close
        yield session


def get_dsr_stores() -> Sequence[ProfileStore]:
    """Wired in main.py (identity must not import the other modules)."""
    raise RuntimeError("DSR stores are not wired")


def get_dsr_service(
    session: Annotated[Session, Depends(get_session)],
    stores: Annotated[Sequence[ProfileStore], Depends(get_dsr_stores)],
) -> DsrService:
    return DsrService(SqlDsrRepository(session), stores)


Service = Annotated[DsrService, Depends(get_dsr_service)]
User = Annotated[Principal, Depends(get_current_user)]


class WithdrawOut(BaseModel):
    type: str
    withdrawn_at: datetime


class EraseIn(BaseModel):
    confirmation: str

    @field_validator("confirmation")
    @classmethod
    def _phrase(cls, v: str) -> str:
        if v != CONFIRM_PHRASE:
            raise ValueError(f"type exactly: {CONFIRM_PHRASE}")
        return v


class ReceiptOut(BaseModel):
    receipt_id: UUID


@router.get("/me/export", responses=_PROBLEMS)
def export_me(user: User, service: Service) -> dict[str, Any]:
    """JSON bundle of everything held about the caller; original-file URLs expire in 15 min."""
    return service.export(user.sub)


@router.post(
    "/me/consents/{consent_type}/withdraw", response_model=WithdrawOut, responses=_PROBLEMS
)
def withdraw_consent(
    consent_type: Annotated[str, Path(pattern=r"^[a-z][a-z0-9_]{0,63}$")],
    user: User,
    service: Service,
) -> WithdrawOut:
    return WithdrawOut(type=consent_type, withdrawn_at=service.withdraw(user.sub, consent_type))


@router.delete("/me", response_model=ReceiptOut, responses=_PROBLEMS)
def erase_me(body: EraseIn, user: User, service: Service) -> ReceiptOut:
    """Irreversible. Idempotent: repeating returns the original receipt."""
    return ReceiptOut(receipt_id=service.erase(user.sub))
