import structlog

from medilens.modules.admin.domain.models import Grant

log = structlog.get_logger()


class LogAlertSink:
    """Structured WARNING picked up by the log-based alarm; ids only, never the reason text."""

    def break_glass_opened(self, grant: Grant) -> None:
        log.warning(
            "break_glass.opened",
            grant_id=str(grant.id),
            admin_sub=grant.admin_sub,
            profile_id=str(grant.profile_id),
            expires_at=grant.expires_at.isoformat(),
        )
