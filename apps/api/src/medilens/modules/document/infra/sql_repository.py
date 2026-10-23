"""PostgreSQL adapters. Run as app_rw; RLS (`app.profile_ids`) is bound per transaction."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles
from medilens.modules.document.domain.models import (
    PENDING_WINDOW_SECONDS,
    STATUS_PENDING,
    STATUS_UPLOADED,
    Document,
    DuplicateDocument,
)


class SqlProfileOwnership:
    """In-DB ownership: profiles whose owner user has this IdP subject."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def owned_profile_ids(self, subject: str) -> list[UUID]:
        rows = self._session.execute(
            text(
                "SELECT p.id FROM identity.patient_profiles p "
                "JOIN identity.users u ON u.id = p.owner_user_id "
                "WHERE u.external_sub = :sub AND p.deleted_at IS NULL AND u.deleted_at IS NULL"
            ),
            {"sub": subject},
        )
        return [r[0] for r in rows]


class SqlDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def scope_to(self, profile_ids: Sequence[UUID]) -> None:
        scope_to_profiles(self._session, profile_ids)

    def new_id(self) -> UUID:
        return self._session.execute(text("SELECT public.uuid_v7()")).scalar_one()

    def add_pending(self, doc: Document) -> None:
        self._session.execute(
            text(
                "INSERT INTO clinical.documents (id, profile_id, storage_key, sha256, mime, status) "
                "VALUES (:id, :p, :k, '', :m, :s)"
            ),
            {
                "id": doc.id,
                "p": doc.profile_id,
                "k": doc.storage_key,
                "m": doc.mime,
                "s": doc.status,
            },
        )

    def get(self, document_id: UUID) -> Document | None:
        row = self._session.execute(
            text(
                "SELECT id, profile_id, storage_key, mime, status, sha256 "
                "FROM clinical.documents WHERE id = :id AND deleted_at IS NULL"
            ),
            {"id": document_id},
        ).first()
        return Document(*row) if row else None

    def count_pending(self) -> int:
        return self._session.execute(
            text(
                "SELECT count(*) FROM clinical.documents "
                "WHERE status = :pending AND deleted_at IS NULL "
                "AND created_at > now() - make_interval(secs => :window)"
            ),
            {"pending": STATUS_PENDING, "window": PENDING_WINDOW_SECONDS},
        ).scalar_one()

    def has_duplicate(self, profile_id: UUID, sha256: str, excluding: UUID) -> bool:
        return bool(
            self._session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM clinical.documents WHERE profile_id = :p "
                    "AND sha256 = :h AND id <> :id AND status <> :pending AND deleted_at IS NULL)"
                ),
                {"p": profile_id, "h": sha256, "id": excluding, "pending": STATUS_PENDING},
            ).scalar_one()
        )

    def mark_uploaded(self, document_id: UUID, sha256: str) -> None:
        try:
            with self._session.begin_nested():
                self._session.execute(
                    text("UPDATE clinical.documents SET status = :s, sha256 = :h WHERE id = :id"),
                    {"s": STATUS_UPLOADED, "h": sha256, "id": document_id},
                )
        except IntegrityError as e:  # ux_documents_profile_sha256: concurrent duplicate
            raise DuplicateDocument("This file was already uploaded for this profile.") from e
