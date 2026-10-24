"""PostgreSQL adapter, run as app_rw under RLS.

Owner paths scope the transaction to the owner's profiles. The grantee has no profile scope, so
the grant is fetched through the narrow definer function `clinical.get_share_grant` (ADR-0006,
migration 0008) and only AFTER a Cedar permit is the transaction scoped to that ONE profile.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles
from medilens.modules.sharing.domain.models import Grant, SharedFinding


class SqlShareRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def resolve_user(self, subject: str) -> UUID | None:
        return self._s.execute(
            text("SELECT id FROM identity.users WHERE external_sub = :s AND deleted_at IS NULL"),
            {"s": subject},
        ).scalar()

    def scope_to_owned(self, user_id: UUID) -> None:
        ids = self._s.execute(
            text(
                "SELECT id FROM identity.patient_profiles "
                "WHERE owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"u": user_id},
        ).scalars()
        scope_to_profiles(self._s, list(ids))

    def owns(self, user_id: UUID, profile_id: UUID) -> bool:
        return (
            self._s.execute(
                text(
                    "SELECT 1 FROM identity.patient_profiles "
                    "WHERE id = :p AND owner_user_id = :u AND deleted_at IS NULL"
                ),
                {"p": profile_id, "u": user_id},
            ).first()
            is not None
        )

    def user_exists(self, user_id: UUID) -> bool:
        return (
            self._s.execute(
                text("SELECT 1 FROM identity.users WHERE id = :u AND deleted_at IS NULL"),
                {"u": user_id},
            ).first()
            is not None
        )

    def insert(self, profile_id: UUID, grantee: UUID, scope: str, expires_at: datetime) -> Grant:
        row = self._s.execute(
            text(
                "INSERT INTO clinical.share_grants (profile_id, grantee_user_id, scope, expires_at) "
                "VALUES (:p, :g, :s, :e) "
                "RETURNING id, profile_id, grantee_user_id, scope, expires_at, revoked_at"
            ),
            {"p": profile_id, "g": grantee, "s": scope, "e": expires_at},
        ).one()
        return Grant(*row)

    def list_for(self, profile_id: UUID) -> list[Grant]:
        rows = self._s.execute(
            text(
                "SELECT id, profile_id, grantee_user_id, scope, expires_at, revoked_at "
                "FROM clinical.share_grants "
                "WHERE profile_id = :p AND deleted_at IS NULL ORDER BY id DESC"
            ),
            {"p": profile_id},
        )
        return [Grant(*r) for r in rows]

    def revoke(self, share_id: UUID, at: datetime) -> bool:
        # RLS limits this to the owner's profiles; a foreign or unknown id matches nothing.
        found = self._s.execute(
            text("SELECT 1 FROM clinical.share_grants WHERE id = :i AND deleted_at IS NULL"),
            {"i": share_id},
        ).first()
        if found is None:
            return False
        self._s.execute(
            text(
                "UPDATE clinical.share_grants SET revoked_at = :t "
                "WHERE id = :i AND revoked_at IS NULL"
            ),
            {"i": share_id, "t": at},
        )
        return True

    def grant_for_grantee(self, share_id: UUID, user_id: UUID) -> Grant | None:
        row = self._s.execute(
            text(
                "SELECT id, profile_id, grantee_user_id, scope, expires_at, revoked_at "
                "FROM clinical.get_share_grant(:i, :u)"
            ),
            {"i": share_id, "u": user_id},
        ).first()
        return Grant(*row) if row else None

    def scope_to(self, profile_id: UUID) -> None:
        scope_to_profiles(self._s, [profile_id])

    def findings(self, profile_id: UUID, after: UUID | None, limit: int) -> list[SharedFinding]:
        rows = self._s.execute(
            text(
                "SELECT bf.id, bf.region_code, bf.laterality, bf.severity, c.unit_code, "
                "bf.is_metastasis, bf.observed_at, c.label "
                "FROM clinical.body_findings bf "
                "JOIN clinical.conditions c ON c.id = bf.condition_id AND c.deleted_at IS NULL "
                "WHERE bf.profile_id = :p AND bf.deleted_at IS NULL "
                "AND (CAST(:after AS uuid) IS NULL OR bf.id < CAST(:after AS uuid)) "
                "ORDER BY bf.id DESC LIMIT :n"
            ),
            {"p": profile_id, "after": after, "n": limit},
        )
        return [SharedFinding(*r) for r in rows]

    def audit(self, actor_id: UUID, action: str, share_id: UUID) -> None:
        self._s.execute(
            text(
                "INSERT INTO audit.audit_events (actor_id, action, resource_type, resource_id) "
                "VALUES (:a, :act, 'share', :r)"
            ),
            {"a": actor_id, "act": action, "r": share_id},
        )

    def commit(self) -> None:
        self._s.commit()
