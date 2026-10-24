"""Data-subject-rights adapter (T106): document metadata + original URLs; erase rows and objects.

S3 objects are deleted before the caller commits: if S3 fails the DB rolls back and the whole
erasure can simply be retried (deletes are idempotent).
"""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.modules.document.domain.ports import DsrStorage

ORIGINAL_URL_TTL_SECONDS = 900
_PER_DOC_PREFIXES = ("raw/{}/", "pre/{}/", "ocr/{}/", "extractions/{}/", "retake/{}")


class SqlDocumentDsr:
    def __init__(self, session: Session, storage: DsrStorage) -> None:
        self._s, self._storage = session, storage
        self._erased_prefixes: list[str] = []

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        rows = self._s.execute(
            text(
                "SELECT id, mime, status, doc_type, pages, uploaded_at FROM clinical.documents "
                "WHERE profile_id = :p AND deleted_at IS NULL ORDER BY id"
            ),
            {"p": profile_id},
        ).mappings()
        return {
            "documents": [
                {
                    **r,
                    "original_url": self._storage.presign_original(
                        profile_id, r["id"], ORIGINAL_URL_TTL_SECONDS
                    ),
                    "original_url_expires_in": ORIGINAL_URL_TTL_SECONDS,
                }
                for r in rows
            ]
        }

    def erase_profile(self, profile_id: UUID) -> None:
        ids = [
            r[0]
            for r in self._s.execute(
                text("SELECT id FROM clinical.documents WHERE profile_id = :p"), {"p": profile_id}
            )
        ]
        for table in ("document_pages", "documents"):
            self._s.execute(
                text(f"DELETE FROM clinical.{table} WHERE profile_id = :p"),  # noqa: S608
                {"p": profile_id},
            )
        self._s.execute(
            text("DELETE FROM worker.document_status WHERE document_id = ANY(:ids)"),
            {"ids": [str(i) for i in ids]},
        )
        prefixes = [f"quarantine/{profile_id}/"]
        prefixes += [p.format(i) for i in ids for p in _PER_DOC_PREFIXES]
        for prefix in prefixes:
            self._storage.delete_prefix(prefix)
        self._erased_prefixes += prefixes

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        out = [
            f"clinical.{t}"
            for t in ("document_pages", "documents")
            if self._s.execute(
                text(f"SELECT 1 FROM clinical.{t} WHERE profile_id = ANY(:ids) LIMIT 1"),  # noqa: S608
                {"ids": profile_ids},
            ).first()
        ]
        # prefixes erased in this request; an idempotent re-run has nothing left to list
        return out + [k for p in self._erased_prefixes for k in self._storage.list_prefix(p)]
