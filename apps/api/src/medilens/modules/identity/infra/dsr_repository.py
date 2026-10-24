"""PostgreSQL adapter for DSR, run as app_rw. Identity rows are deleted only through the definer
function identity.erase_user (migration 0010)."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles


class SqlDsrRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def resolve(self, subject: str) -> UUID | None:
        # soft-deleted users are still users here: erasure must reach them
        return self._s.execute(
            text("SELECT id FROM identity.users WHERE external_sub = :s"), {"s": subject}
        ).scalar()

    def profiles(self, user_id: UUID) -> list[dict[str, Any]]:
        rows = self._s.execute(
            text(
                "SELECT id, birth_year, sex_at_birth, is_minor FROM identity.patient_profiles "
                "WHERE owner_user_id = :u ORDER BY id"
            ),
            {"u": user_id},
        ).mappings()
        return [dict(r) for r in rows]

    def scope_to(self, profile_ids: list[UUID]) -> None:
        scope_to_profiles(self._s, profile_ids)

    def consents(self, user_id: UUID) -> list[dict[str, Any]]:
        rows = self._s.execute(
            text(
                "SELECT id, type, terms_version, given_at, withdrawn_at "
                "FROM identity.consents WHERE user_id = :u ORDER BY id"
            ),
            {"u": user_id},
        ).mappings()
        return [dict(r) for r in rows]

    def withdraw(self, user_id: UUID, consent_type: str) -> datetime | None:
        self._s.execute(
            text(
                "UPDATE identity.consents SET withdrawn_at = now() "
                "WHERE user_id = :u AND type = :t AND withdrawn_at IS NULL"
            ),
            {"u": user_id, "t": consent_type},
        )
        return self._s.execute(
            text(
                "SELECT max(withdrawn_at) FROM identity.consents WHERE user_id = :u AND type = :t"
            ),
            {"u": user_id, "t": consent_type},
        ).scalar()

    def new_id(self) -> UUID:
        return self._s.execute(text("SELECT public.uuid_v7()")).scalar_one()

    def erase_user(self, user_id: UUID, salt: str) -> None:
        self._s.execute(text("SELECT identity.erase_user(:u, :s)"), {"u": user_id, "s": salt})

    def leftovers(self, user_id: UUID, profile_ids: list[UUID]) -> list[str]:
        checks = {
            "identity.users": (text("SELECT 1 FROM identity.users WHERE id = :u LIMIT 1"), {}),
            "identity.patient_profiles": (
                text("SELECT 1 FROM identity.patient_profiles WHERE owner_user_id = :u LIMIT 1"),
                {},
            ),
            "identity.consents": (
                text("SELECT 1 FROM identity.consents WHERE user_id = :u LIMIT 1"),
                {},
            ),
            "clinical.share_grants (grantee)": (
                text("SELECT 1 FROM clinical.share_grants WHERE grantee_user_id = :u LIMIT 1"),
                {},
            ),
            "audit.break_glass_grants": (
                text("SELECT 1 FROM audit.break_glass_grants WHERE profile_id = ANY(:ids) LIMIT 1"),
                {"ids": profile_ids},
            ),
            "audit.audit_events (unpseudonymised actor)": (
                text("SELECT 1 FROM audit.audit_events WHERE actor_id = :u LIMIT 1"),
                {},
            ),
        }
        out = [
            name
            for name, (stmt, extra) in checks.items()
            if self._s.execute(stmt, {"u": user_id, **extra}).first()
        ]
        # clinical.outbox has no profile column; its payload carries profile_id
        if self._s.execute(
            text(
                "SELECT 1 FROM clinical.outbox WHERE payload ->> 'profile_id' = ANY(:ids) LIMIT 1"
            ),
            {"ids": [str(p) for p in profile_ids]},
        ).first():
            out.append("clinical.outbox")
        return out

    def receipt_for(self, subject_hash: str) -> UUID | None:
        return self._s.execute(
            text(
                "SELECT id FROM audit.erasure_receipts WHERE subject_hash = :h "
                "ORDER BY created_at DESC LIMIT 1"
            ),
            {"h": subject_hash},
        ).scalar()

    def add_receipt(self, receipt_id: UUID, subject_hash: str, summary: dict[str, Any]) -> None:
        self._s.execute(
            text(
                "INSERT INTO audit.erasure_receipts (id, subject_hash, summary) "
                "VALUES (:i, :h, CAST(:s AS jsonb))"
            ),
            {"i": receipt_id, "h": subject_hash, "s": json.dumps(summary)},
        )

    def audit(self, actor_id: UUID | None, action: str, resource_id: UUID | None) -> None:
        self._s.execute(
            text(
                "INSERT INTO audit.audit_events (actor_id, action, resource_type, resource_id) "
                "VALUES (:a, :act, 'dsr', :r)"
            ),
            {"a": actor_id, "act": action, "r": resource_id},
        )

    def commit(self) -> None:
        self._s.commit()
