"""PostgreSQL + pgvector adapter. Run as app_rw; RLS (`app.profile_ids`) is bound per transaction."""

import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles
from medilens.modules.knowledge.domain.models import Chunk, Hit

_INSERT = text(
    "INSERT INTO clinical.knowledge_chunks "
    "(profile_id, article_id, language, source_ref, title, content, citations, reviewed, "
    "embedding) VALUES (:p, :a, :l, :s, :t, :c, CAST(:cit AS jsonb), :r, CAST(:e AS vector))"
)


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


class SqlKnowledgeRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def resolve(self, subject: str) -> UUID | None:
        user = self._s.execute(
            text("SELECT id FROM identity.users WHERE external_sub = :s AND deleted_at IS NULL"),
            {"s": subject},
        ).scalar()
        if user is None:
            return None
        ids = self._s.execute(
            text(
                "SELECT id FROM identity.patient_profiles "
                "WHERE owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"u": user},
        ).scalars()
        scope_to_profiles(self._s, list(ids))
        return user

    def owns(self, user_id: UUID, profile_id: UUID) -> bool:
        row = self._s.execute(
            text(
                "SELECT 1 FROM identity.patient_profiles "
                "WHERE id = :p AND owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"p": profile_id, "u": user_id},
        ).first()
        return row is not None

    def _insert(self, profile_id: UUID | None, rows: list[tuple[Chunk, list[float]]]) -> None:
        for c, vec in rows:
            self._s.execute(
                _INSERT,
                {
                    "p": profile_id,
                    "a": c.article_id,
                    "l": c.language,
                    "s": c.source_ref,
                    "t": c.title,
                    "c": c.content,
                    "cit": json.dumps(c.citations),
                    "r": c.reviewed,
                    "e": _vec(vec),
                },
            )

    def replace_article(self, article_id: str, chunks: list[tuple[Chunk, list[float]]]) -> None:
        # Ingest runs as the migrator/superuser: only it may write public (profile_id NULL) rows.
        self._s.execute(
            text(
                "DELETE FROM clinical.knowledge_chunks WHERE article_id = :a AND profile_id IS NULL"
            ),
            {"a": article_id},
        )
        self._insert(None, chunks)

    def replace_profile_text(
        self, profile_id: UUID, source_ref: str, chunks: list[tuple[Chunk, list[float]]]
    ) -> None:
        scope_to_profiles(self._s, [profile_id])
        self._s.execute(
            text("DELETE FROM clinical.knowledge_chunks WHERE profile_id = :p AND source_ref = :s"),
            {"p": profile_id, "s": source_ref},
        )
        self._insert(profile_id, chunks)

    def search(
        self, profile_id: UUID, vector: list[float], k: int, allow_drafts: bool
    ) -> list[Hit]:
        rows = self._s.execute(
            text(
                "SELECT content, article_id, language, title, citations, profile_id, "
                "embedding <=> CAST(:v AS vector) AS dist "
                "FROM clinical.knowledge_chunks "
                "WHERE (profile_id IS NULL OR profile_id = :p) AND (reviewed OR :d) "
                "ORDER BY dist, id LIMIT :k"
            ),
            {"v": _vec(vector), "p": profile_id, "d": allow_drafts, "k": k},
        )
        return [Hit(*r) for r in rows]
