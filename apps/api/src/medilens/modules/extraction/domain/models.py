"""Extraction review rules (BR-012) and errors. Pure: no framework types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from medilens.core.errors import AppError, NotFound

CONFIRM_THRESHOLD = 0.7  # BR-012: below this the user must confirm the field
MAX_USER_VALUE_LEN = 2000
RUN_CONFIRMED = "confirmed"
ACTION_CONFIRM = "extraction.confirm"
ACTION_EDIT = "extraction.edit_field"


@dataclass(frozen=True)
class FieldView:
    id: UUID
    field_path: str
    value: str | None
    user_value: str | None
    confidence: float | None
    source_page: int | None
    source_box: Any
    confirmed_at: datetime | None

    @property
    def needs_confirmation(self) -> bool:
        return self.confidence is not None and self.confidence < CONFIRM_THRESHOLD


class ExtractionNotFound(NotFound):
    """Also used for other users' documents/fields: existence is never leaked."""

    def __init__(self) -> None:
        super().__init__("Resource not found.")


class UnconfirmedFields(AppError):
    status = 409
    code = "MEDILENS-409"
    slug = "unconfirmed-fields"
    title = "Unconfirmed fields remain"

    def __init__(self, field_ids: list[UUID]) -> None:
        super().__init__(
            "Confirm these low-confidence fields first: " + ", ".join(map(str, field_ids))
        )


class ReviewRepository(Protocol):
    def resolve(self, subject: str) -> UUID | None:
        """The caller's user id; binds the transaction's RLS scope to their profiles."""

    def latest_run(self, document_id: UUID) -> UUID | None: ...
    def fields(self, run_id: UUID) -> list[FieldView]: ...
    def set_user_value(self, run_id: UUID, field_id: UUID, value: str) -> FieldView | None: ...
    def mark_confirmed(self, run_id: UUID) -> None: ...
    def audit(self, actor_id: UUID, action: str, resource_type: str, resource_id: UUID) -> None: ...
