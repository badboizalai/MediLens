from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from medilens.core.errors import Forbidden, NotFound
from medilens.modules.admin.domain.models import (
    BREAK_GLASS_TTL,
    AdminRepository,
    AlertSink,
    DocumentMeta,
    Grant,
)


class AdminService:
    def __init__(
        self,
        repo: AdminRepository,
        alerts: AlertSink,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._repo, self._alerts, self._now = repo, alerts, now

    def stats(self) -> dict[str, int]:
        return self._repo.stats()

    def open_break_glass(
        self, admin_sub: str, profile_id: UUID, reason: str, ticket: str | None
    ) -> Grant:
        if not self._repo.profile_exists(profile_id):
            raise NotFound("Profile not found")
        grant = self._repo.create_grant(
            admin_sub, profile_id, reason, ticket, self._now() + BREAK_GLASS_TTL
        )
        self._repo.audit(admin_sub, "break_glass.opened", "break_glass_grant", grant.id)
        self._alerts.break_glass_opened(grant)  # raising here rolls the grant back (fail closed)
        return grant

    def list_documents(self, admin_sub: str, grant_id: UUID) -> list[DocumentMeta]:
        grant = self._repo.get_grant(grant_id)
        if grant is None or not grant.is_active_for(admin_sub, self._now()):
            raise Forbidden("No active break-glass grant")
        docs = self._repo.documents_for_grant(grant_id, admin_sub)
        self._repo.audit(admin_sub, "break_glass.read_documents", "break_glass_grant", grant_id)
        return docs
