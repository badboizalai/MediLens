# ruff: noqa: S608  (f-strings interpolate only the module-constant column list)
"""PostgreSQL adapter. Run as app_rw; RLS (`app.profile_ids`) is bound per transaction.

Ownership and audit are small SQL statements here because the import-linter contract keeps
modules independent (no import of the identity/document/audit services).
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles
from medilens.modules.extraction.domain.models import RUN_CONFIRMED, FieldView

_COLS = "id, field_path, value, user_value, confidence, source_page, source_box, confirmed_at"


class SqlReviewRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def resolve(self, subject: str) -> UUID | None:
        user = self._session.execute(
            text("SELECT id FROM identity.users WHERE external_sub = :s AND deleted_at IS NULL"),
            {"s": subject},
        ).scalar()
        if user is None:
            return None
        ids = self._session.execute(
            text(
                "SELECT id FROM identity.patient_profiles "
                "WHERE owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"u": user},
        ).scalars()
        scope_to_profiles(self._session, list(ids))
        return user

    def latest_run(self, document_id: UUID) -> UUID | None:
        return self._session.execute(
            text(
                "SELECT id FROM clinical.extraction_runs "
                "WHERE document_id = :d AND deleted_at IS NULL "
                "ORDER BY id DESC LIMIT 1"  # uuid_v7: id order is creation order
            ),
            {"d": document_id},
        ).scalar()

    def fields(self, run_id: UUID) -> list[FieldView]:
        rows = self._session.execute(
            text(
                f"SELECT {_COLS} FROM clinical.extraction_fields "
                "WHERE run_id = :r AND deleted_at IS NULL ORDER BY id"
            ),
            {"r": run_id},
        )
        return [FieldView(*r) for r in rows]

    def set_user_value(self, run_id: UUID, field_id: UUID, value: str) -> FieldView | None:
        row = self._session.execute(
            text(
                "UPDATE clinical.extraction_fields SET user_value = :v, confirmed_at = now() "
                f"WHERE id = :f AND run_id = :r AND deleted_at IS NULL RETURNING {_COLS}"
            ),
            {"v": value, "f": field_id, "r": run_id},
        ).first()
        return FieldView(*row) if row else None

    def mark_confirmed(self, run_id: UUID) -> None:
        self._session.execute(
            text("UPDATE clinical.extraction_runs SET status = :s WHERE id = :r"),
            {"s": RUN_CONFIRMED, "r": run_id},
        )

    def audit(self, actor_id: UUID, action: str, resource_type: str, resource_id: UUID) -> None:
        self._session.execute(
            text(
                "INSERT INTO audit.audit_events (actor_id, action, resource_type, resource_id) "
                "VALUES (:a, :act, :t, :r)"
            ),
            {"a": actor_id, "act": action, "t": resource_type, "r": resource_id},
        )
