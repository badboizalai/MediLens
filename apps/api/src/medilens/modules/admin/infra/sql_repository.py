from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.modules.admin.domain.models import DocumentMeta, Grant

_GET_GRANT = (
    "SELECT id, admin_sub, profile_id, expires_at, revoked_at "
    "FROM audit.break_glass_grants WHERE id = :g"
)


class SqlAdminRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def stats(self) -> dict[str, int]:
        rows = self._s.execute(text("SELECT metric, n FROM audit.admin_stats()"))
        return {m: int(n) for m, n in rows}

    def profile_exists(self, profile_id: UUID) -> bool:
        sql = "SELECT 1 FROM identity.patient_profiles WHERE id = :p AND deleted_at IS NULL"
        return self._s.execute(text(sql), {"p": profile_id}).first() is not None

    def create_grant(
        self,
        admin_sub: str,
        profile_id: UUID,
        reason: str,
        ticket: str | None,
        expires_at: datetime,
    ) -> Grant:
        row = self._s.execute(
            text(
                "INSERT INTO audit.break_glass_grants "
                "(admin_sub, profile_id, reason, ticket, expires_at) "
                "VALUES (:a, :p, :r, :t, :e) RETURNING id, admin_sub, profile_id, expires_at, revoked_at"
            ),
            {"a": admin_sub, "p": profile_id, "r": reason, "t": ticket, "e": expires_at},
        ).one()
        return Grant(*row)

    def get_grant(self, grant_id: UUID) -> Grant | None:
        row = self._s.execute(
            text(_GET_GRANT),
            {"g": grant_id},
        ).first()
        return Grant(*row) if row else None

    def documents_for_grant(self, grant_id: UUID, admin_sub: str) -> list[DocumentMeta]:
        rows = self._s.execute(
            text("SELECT id, status FROM audit.break_glass_documents(:g, :a)"),
            {"g": grant_id, "a": admin_sub},
        )
        return [DocumentMeta(*r) for r in rows]

    def audit(self, admin_sub: str, action: str, resource_type: str, resource_id: UUID) -> None:
        self._s.execute(
            text(
                "INSERT INTO audit.audit_events (actor_id, action, resource_type, resource_id) "
                "VALUES ((SELECT id FROM identity.users WHERE external_sub = :a), :act, :rt, :rid)"
            ),
            {"a": admin_sub, "act": action, "rt": resource_type, "rid": resource_id},
        )
