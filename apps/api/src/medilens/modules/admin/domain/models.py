"""Break-glass grant (SEC-AZ-05). Ids and timestamps only: nothing here is PHI."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol
from uuid import UUID

BREAK_GLASS_TTL = timedelta(hours=1)  # fixed by SEC-AZ-05, not configurable
MIN_REASON_LEN = 10


@dataclass(frozen=True)
class Grant:
    id: UUID
    admin_sub: str
    profile_id: UUID
    expires_at: datetime
    revoked_at: datetime | None = None

    def is_active_for(self, admin_sub: str, now: datetime) -> bool:
        return self.admin_sub == admin_sub and self.revoked_at is None and now < self.expires_at


@dataclass(frozen=True)
class DocumentMeta:
    id: UUID
    status: str


class AlertSink(Protocol):
    def break_glass_opened(self, grant: Grant) -> None: ...


class AdminRepository(Protocol):
    def stats(self) -> dict[str, int]: ...
    def profile_exists(self, profile_id: UUID) -> bool: ...
    def create_grant(
        self,
        admin_sub: str,
        profile_id: UUID,
        reason: str,
        ticket: str | None,
        expires_at: datetime,
    ) -> Grant: ...
    def get_grant(self, grant_id: UUID) -> Grant | None: ...
    def documents_for_grant(self, grant_id: UUID, admin_sub: str) -> list[DocumentMeta]: ...
    def audit(self, admin_sub: str, action: str, resource_type: str, resource_id: UUID) -> None: ...
