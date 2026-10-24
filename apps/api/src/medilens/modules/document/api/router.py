import json
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.db import make_engine, make_session_factory
from medilens.modules.document.application.service import UploadService
from medilens.modules.document.application.status_stream import Clock, watch_status
from medilens.modules.document.domain.models import (
    DocumentNotFound,
    DuplicateDocument,
    FileTooLarge,
    UnsupportedFileType,
)
from medilens.modules.document.domain.ports import DsrStorage, ObjectStorage, PageImages
from medilens.modules.document.infra.s3_storage import (
    S3DsrStorage,
    S3PageImages,
    S3Storage,
    get_storage_settings,
)
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
    429: {"description": "Too many pending uploads"},
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


PAGE_URL_TTL_SECONDS = 300


class PageImageOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    url: str
    expires_in: int = Field(serialization_alias="expiresIn")


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


@lru_cache
def get_page_images() -> PageImages:
    return S3PageImages(get_storage_settings())


@lru_cache
def get_dsr_storage() -> DsrStorage:
    return S3DsrStorage(get_storage_settings())


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
    try:
        doc = service.complete(user.sub, document_id)
    except (FileTooLarge, UnsupportedFileType, DuplicateDocument):
        session.commit()  # keep the 'rejected' status; the problem response still goes out
        raise
    session.commit()  # status change and outbox row land together
    return DocumentOut(id=doc.id, profile_id=doc.profile_id, status=doc.status)


@router.get("/documents/{document_id}", response_model=DocumentOut, responses=_PROBLEMS)
def get_document(
    document_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[UploadService, Depends(get_service)],
) -> DocumentOut:
    doc = service.get(user.sub, document_id)
    return DocumentOut(id=doc.id, profile_id=doc.profile_id, status=doc.status)


@router.get(
    "/documents/{document_id}/pages/{page_no}/image",
    response_model=PageImageOut,
    responses=_PROBLEMS,
)
def get_page_image(
    document_id: UUID,
    page_no: int,
    response: Response,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[UploadService, Depends(get_service)],
    pages: Annotated[PageImages, Depends(get_page_images)],
) -> PageImageOut:
    service.get(user.sub, document_id)  # owner-only: anyone else gets the same 404
    url = pages.presign_page(document_id, page_no, PAGE_URL_TTL_SECONDS) if page_no >= 1 else None
    if url is None:
        raise DocumentNotFound
    response.headers["Cache-Control"] = "no-store"
    return PageImageOut(url=url, expires_in=PAGE_URL_TTL_SECONDS)


def get_clock() -> Clock:
    return Clock()


@router.get(
    "/documents/{document_id}/events",
    responses={
        **_PROBLEMS,
        200: {
            "description": "Server-Sent Events: `event: status` with `{status, updatedAt}` "
            "(updatedAt = when the API observed it) first, then on every change; "
            "`: keep-alive` comments; closes on a terminal status or after 5 minutes.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        },
    },
)
def document_events(
    document_id: UUID,
    user: Annotated[Principal, Depends(get_current_user)],
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
    storage: Annotated[ObjectStorage, Depends(get_storage)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> StreamingResponse:
    def poll() -> str | None:
        with factory() as session:  # short transaction per poll: no connection held while idle
            service = UploadService(
                storage,
                SqlDocumentRepository(session),
                SqlProfileOwnership(session),
                SqlOutbox(session),
            )
            try:
                return service.get(user.sub, document_id).status
            except DocumentNotFound:
                return None

    if poll() is None:  # 404 as a normal Problem Details response, before the stream starts
        raise DocumentNotFound

    async def frames() -> AsyncIterator[str]:
        async for status in watch_status(poll, clock):
            if status is None:
                yield ": keep-alive\n\n"
                continue
            data = {"status": status, "updatedAt": datetime.now(timezone.utc).isoformat()}
            yield f"event: status\ndata: {json.dumps(data)}\n\n"

    return StreamingResponse(
        frames(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )
