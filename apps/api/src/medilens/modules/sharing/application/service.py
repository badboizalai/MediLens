from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID

from medilens.modules.sharing.domain.models import (
    ACTION_READ,
    MAX_EXPIRES_HOURS,
    SCOPE_FINDINGS_READ,
    Grant,
    ShareAuthorizer,
    ShareDenied,
    SharedFinding,
    ShareNotFound,
    ShareRepository,
)

MAX_LIMIT = 100


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SharingService:
    """Commits its own transactions. Audit rows hold ids only."""

    def __init__(
        self,
        repo: ShareRepository,
        authorizer: ShareAuthorizer,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repo, self._authz, self._clock = repo, authorizer, clock

    def _owner(self, subject: str) -> UUID:
        user = self._repo.resolve_user(subject)
        if user is None:
            raise ShareNotFound
        self._repo.scope_to_owned(user)
        return user

    def create(self, subject: str, profile_id: UUID, grantee: UUID, hours: int) -> Grant:
        user = self._owner(subject)
        if not self._repo.owns(user, profile_id) or not self._repo.user_exists(grantee):
            raise ShareNotFound
        hours = max(1, min(hours, MAX_EXPIRES_HOURS))
        expires = self._clock() + timedelta(hours=hours)
        grant = self._repo.insert(profile_id, grantee, SCOPE_FINDINGS_READ, expires)
        self._repo.audit(user, "share.create", grant.id)
        self._repo.commit()
        return grant

    def list_shares(self, subject: str, profile_id: UUID) -> list[Grant]:
        user = self._owner(subject)
        if not self._repo.owns(user, profile_id):
            raise ShareNotFound
        return self._repo.list_for(profile_id)

    def revoke(self, subject: str, share_id: UUID) -> None:
        user = self._owner(subject)
        if not self._repo.revoke(share_id, self._clock()):
            raise ShareNotFound
        self._repo.audit(user, "share.revoke", share_id)
        self._repo.commit()

    def _permitted_grant(self, subject: str, share_id: UUID) -> tuple[UUID, Grant]:
        user = self._repo.resolve_user(subject)
        grant = self._repo.grant_for_grantee(share_id, user) if user else None
        if user is None or grant is None:
            raise ShareNotFound  # not the grantee: indistinguishable from unknown
        if not self._authz.is_permitted(user, ACTION_READ, grant, self._clock()):
            self._repo.audit(user, "share.use_denied", share_id)
            self._repo.commit()
            raise ShareDenied
        return user, grant

    def get_share(self, subject: str, share_id: UUID) -> Grant:
        return self._permitted_grant(subject, share_id)[1]

    def read_findings(
        self, subject: str, share_id: UUID, cursor: UUID | None, limit: int
    ) -> tuple[list[SharedFinding], UUID | None]:
        user, grant = self._permitted_grant(subject, share_id)
        self._repo.scope_to(grant.profile_id)  # this request, this one profile
        self._repo.audit(user, "share.use", share_id)
        limit = max(1, min(limit, MAX_LIMIT))
        rows = self._repo.findings(grant.profile_id, cursor, limit + 1)
        nxt = rows[limit - 1].id if len(rows) > limit else None
        self._repo.commit()
        return rows[:limit], nxt
