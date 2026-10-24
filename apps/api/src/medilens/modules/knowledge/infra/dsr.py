"""Data-subject-rights adapter (T106): per-profile knowledge chunks hold record text."""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class SqlKnowledgeDsr:
    def __init__(self, session: Session) -> None:
        self._s = session

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        n = self._s.execute(
            text("SELECT count(*) FROM clinical.knowledge_chunks WHERE profile_id = :p"),
            {"p": profile_id},
        ).scalar_one()
        return {"knowledge_chunks": n}  # derived search index of the record text, counted only

    def erase_profile(self, profile_id: UUID) -> None:
        self._s.execute(
            text("DELETE FROM clinical.knowledge_chunks WHERE profile_id = :p"), {"p": profile_id}
        )

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        found = self._s.execute(
            text("SELECT 1 FROM clinical.knowledge_chunks WHERE profile_id = ANY(:ids) LIMIT 1"),
            {"ids": profile_ids},
        ).first()
        return ["clinical.knowledge_chunks"] if found else []
