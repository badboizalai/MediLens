"""Sharing domain: a grant of read access to one profile's findings. Pure, no framework types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from medilens.core.errors import Forbidden, NotFound

SCOPE_FINDINGS_READ = "findings:read"
MAX_EXPIRES_HOURS = 168  # 7 days
ACTION_READ = "read"


class ShareNotFound(NotFound):
    """Also for other people's shares: existence is never leaked."""

    def __init__(self) -> None:
        super().__init__("Resource not found.")


class ShareDenied(Forbidden):
    """Expired, revoked or out-of-scope share."""

    def __init__(self) -> None:
        super().__init__("This share is no longer valid.")


@dataclass(frozen=True)
class Grant:
    id: UUID
    profile_id: UUID
    grantee_user_id: UUID
    scope: str
    expires_at: datetime
    revoked_at: datetime | None


@dataclass(frozen=True)
class SharedFinding:
    id: UUID
    region_code: str
    laterality: str | None
    severity: str | None
    unit_code: str | None
    is_metastasis: bool
    observed_at: datetime | None
    label: str | None


class ShareAuthorizer(Protocol):
    def is_permitted(self, user_id: UUID, action: str, grant: Grant, now: datetime) -> bool: ...


class ShareRepository(Protocol):
    def resolve_user(self, subject: str) -> UUID | None: ...
    def scope_to_owned(self, user_id: UUID) -> None: ...
    def owns(self, user_id: UUID, profile_id: UUID) -> bool: ...
    def user_exists(self, user_id: UUID) -> bool: ...
    def insert(
        self, profile_id: UUID, grantee: UUID, scope: str, expires_at: datetime
    ) -> Grant: ...
    def list_for(self, profile_id: UUID) -> list[Grant]: ...
    def revoke(self, share_id: UUID, at: datetime) -> bool: ...
    def grant_for_grantee(self, share_id: UUID, user_id: UUID) -> Grant | None: ...
    def scope_to(self, profile_id: UUID) -> None: ...
    def findings(self, profile_id: UUID, after: UUID | None, limit: int) -> list[SharedFinding]: ...
    def audit(self, actor_id: UUID, action: str, share_id: UUID) -> None: ...
    def commit(self) -> None: ...
