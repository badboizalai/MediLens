from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from medilens.modules.document.domain.models import Document, Presigned


class ObjectStorage(Protocol):
    def presign_put(
        self, key: str, content_type: str, size_bytes: int, expires_in: int
    ) -> Presigned: ...

    def size(self, key: str) -> int | None:
        """Object size in bytes, or None when absent."""

    def read_head(self, key: str, n: int) -> bytes:
        """First n bytes (ranged GET)."""

    def sha256(self, key: str) -> str:
        """Hex digest, streamed."""

    def delete(self, key: str) -> None: ...


class PageImages(Protocol):
    def presign_page(self, document_id: UUID, page_no: int, expires_in: int) -> str | None:
        """Short-lived GET URL for a processed page image, or None when that page is absent."""


class ProfileOwnership(Protocol):
    def owned_profile_ids(self, subject: str) -> Sequence[UUID]: ...


class DocumentRepository(Protocol):
    def scope_to(self, profile_ids: Sequence[UUID]) -> None:
        """Bind RLS for the current transaction."""

    def new_id(self) -> UUID: ...

    def add_pending(self, doc: Document) -> None: ...

    def get(self, document_id: UUID) -> Document | None:
        """None when absent or outside the RLS scope."""

    def count_pending(self) -> int:
        """Pending (not yet completed) documents inside the RLS scope."""

    def has_duplicate(self, profile_id: UUID, sha256: str, excluding: UUID) -> bool: ...

    def mark_uploaded(self, document_id: UUID, sha256: str) -> None:
        """Raises DuplicateDocument when a concurrent upload won the unique index."""

    def mark_rejected(self, document_id: UUID) -> None: ...

    def apply_status(self, document_id: UUID, status: str) -> str:
        """Forward-only worker status change; `applied` | `ignored` | `unknown`. No RLS scope."""


class EventOutbox(Protocol):
    def add(self, event_type: str, payload: dict[str, Any]) -> None: ...
