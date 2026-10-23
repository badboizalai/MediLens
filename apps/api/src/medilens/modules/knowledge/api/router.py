from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker

from medilens.core.config import get_settings
from medilens.core.db import make_engine, make_session_factory
from medilens.modules.knowledge.application.service import MAX_K, KnowledgeService
from medilens.modules.knowledge.infra.hashing_embedder import HashingEmbedder
from medilens.modules.knowledge.infra.sql_repository import SqlKnowledgeRepository
from medilens.shared.auth import Principal, get_current_user

router = APIRouter(tags=["knowledge"])

_PROBLEMS = {
    400: {"description": "Validation failed"},
    401: {"description": "Unauthenticated"},
    404: {"description": "Not found"},
}


class SearchIn(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    k: int = Field(default=5, ge=1, le=MAX_K)


class ChunkOut(BaseModel):
    content: str
    article_id: str | None
    language: str | None
    title: str | None
    citations: list[dict[str, Any]]
    scope: str  # "article" | "profile"
    distance: float


class SearchOut(BaseModel):
    chunks: list[ChunkOut]


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return make_session_factory(make_engine())


def get_session(
    factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with factory() as session:
        yield session


def get_allow_drafts() -> bool:
    return get_settings().knowledge_allow_drafts


def get_service(
    session: Annotated[Session, Depends(get_session)],
    allow_drafts: Annotated[bool, Depends(get_allow_drafts)],
) -> KnowledgeService:
    return KnowledgeService(SqlKnowledgeRepository(session), HashingEmbedder(), allow_drafts)


@router.post(
    "/profiles/{profile_id}/knowledge/search", response_model=SearchOut, responses=_PROBLEMS
)
def search(
    profile_id: UUID,
    body: SearchIn,
    user: Annotated[Principal, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(get_service)],
) -> SearchOut:
    hits = service.search(user.sub, profile_id, body.query, body.k)
    return SearchOut(
        chunks=[
            ChunkOut(
                content=h.content,
                article_id=h.article_id,
                language=h.language,
                title=h.title,
                citations=h.citations,
                scope="article" if h.profile_id is None else "profile",
                distance=h.distance,
            )
            for h in hits
        ]
    )
