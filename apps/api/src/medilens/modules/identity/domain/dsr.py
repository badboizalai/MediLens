"""Data subject rights (T106; Law 91/2025/QH15, Decree 356/2025): ports and errors."""

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from medilens.core.errors import NotFound

CONFIRM_PHRASE = "DELETE MY ACCOUNT"


class UserNotFound(NotFound):
    """No such account (or it was already erased and left no receipt)."""


class ConsentNotFound(NotFound):
    pass


class ProfileStore(Protocol):
    """One module's per-profile personal data. Implemented by the other modules' infra and
    wired in main.py, so identity never imports them."""

    def export_profile(self, profile_id: UUID) -> dict[str, Any]: ...

    def erase_profile(self, profile_id: UUID) -> None: ...

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        """Names of anything still holding data of these (already erased) profiles."""


class DsrRepository(Protocol):
    def resolve(self, subject: str) -> UUID | None: ...

    def profiles(self, user_id: UUID) -> list[dict[str, Any]]:
        """Own profiles, soft-deleted ones included."""

    def scope_to(self, profile_ids: list[UUID]) -> None: ...

    def consents(self, user_id: UUID) -> list[dict[str, Any]]: ...

    def withdraw(self, user_id: UUID, consent_type: str) -> datetime | None:
        """Sets withdrawn_at on active consents of that type; None when the user has none."""

    def new_id(self) -> UUID: ...

    def erase_user(self, user_id: UUID, salt: str) -> None:
        """Identity rows, grants, outbox events; audit actor ids pseudonymised."""

    def leftovers(self, user_id: UUID, profile_ids: list[UUID]) -> list[str]: ...

    def receipt_for(self, subject_hash: str) -> UUID | None: ...

    def add_receipt(self, receipt_id: UUID, subject_hash: str, summary: dict[str, Any]) -> None: ...

    def audit(self, actor_id: UUID | None, action: str, resource_id: UUID | None) -> None: ...

    def commit(self) -> None: ...
