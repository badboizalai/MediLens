"""Data-subject-rights adapter (T106): shares the owner gave are exported, then hard-deleted.

Deleting the row revokes access at once (Cedar finds no grant). Grants the user received as a
grantee are removed by identity.erase_user.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class SqlSharingDsr:
    def __init__(self, session: Session) -> None:
        self._s = session

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        rows = self._s.execute(
            text(
                "SELECT id, grantee_user_id, scope, expires_at, revoked_at "
                "FROM clinical.share_grants WHERE profile_id = :p ORDER BY id"
            ),
            {"p": profile_id},
        ).mappings()
        return {"shares": [dict(r) for r in rows]}

    def erase_profile(self, profile_id: UUID) -> None:
        self._s.execute(
            text("DELETE FROM clinical.share_grants WHERE profile_id = :p"), {"p": profile_id}
        )

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        found = self._s.execute(
            text("SELECT 1 FROM clinical.share_grants WHERE profile_id = ANY(:ids) LIMIT 1"),
            {"ids": profile_ids},
        ).first()
        return ["clinical.share_grants"] if found else []
