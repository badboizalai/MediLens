from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.document.application.service import UploadService
from medilens.modules.document.domain.ports import ObjectStorage
from medilens.modules.document.infra.s3_storage import S3Storage, get_storage_settings
from medilens.modules.document.infra.sql_repository import (
    SqlDocumentRepository,
    SqlProfileOwnership,
)
from medilens.shared.auth import Principal, get_current_user
from medilens.shared.outbox import SqlOutbox

router = APIRouter(tags=["documents"])

_PROBLEMS = {
    400: {"description": "Validation failed"},
    401: {"description": "Unauthenticated"},
    404: {"description": "Not found"},
    409: {"description": "Duplicate or missing upload"},
    413: {"description": "File too large"},
    415: {"description": "Unsupported file type"},
}


class UploadRequest(BaseModel):
    content_type: str = Field(examples=["application/pdf"])
    size_bytes: int = Field(gt=0)  # oversize is a 413 business rule, not a 400


class UploadResponse(BaseModel):
    document_id: UUID
    upload_url: str
    method: str = "PUT"
    headers: dict[str, str]
    expires_in: int


class DocumentOut(BaseModel):
    id: UUID
    profile_id: UUID
    status: str


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:  # uncommitted work is rolled back on close
        yield session


@lru_cache
def get_storage() -> ObjectStorage:
    return S3Storage(get_storage_settings())


def get_service(
    session: Annotated[Session, Depends(get_session)],
    storage: Annotated[ObjectStorage, Depends(get_storage)],
) -> UploadService:
    return UploadService(
        storage, SqlDocumentRepository(session), SqlProfileOwnership(session), SqlOutbox(session)
    )


@router.post(
    "/profiles/{profile_id}/documents",
    response_model=UploadResponse,
    status_code=201,
    responses=_PROBLEMS,
)
def request_upload(
    profile_id: UUID,
    body: UploadRequest,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[UploadService, Depends(get_service)],
    session: Annotated[Session, Depends(get_session)],
) -> UploadResponse:
    doc, presigned = service.request_upload(
        user.sub, profile_id, body.content_type, body.size_bytes
    )
    session.commit()
    return UploadResponse(
        document_id=doc.id,
        upload_url=presigned.url,
        headers=presigned.headers,
        expires_in=presigned.expires_in,
    )


@router.post("/documents/{document_id}/complete", response_model=DocumentOut, responses=_PROBLEMS)
def complete_upload(
    document_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[UploadService, Depends(get_service)],
    session: Annotated[Session, Depends(get_session)],
) -> DocumentOut:
    doc = service.complete(user.sub, document_id)
    session.commit()  # status change and outbox row land together
    return DocumentOut(id=doc.id, profile_id=doc.profile_id, status=doc.status)
