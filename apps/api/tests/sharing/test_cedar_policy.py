"""Decision table for share.cedar (no database)."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from medilens.modules.sharing.domain.models import Grant
from medilens.modules.sharing.infra.cedar import CedarShareAuthorizer

NOW = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
BOB = uuid4()
GRANT = Grant(uuid4(), uuid4(), BOB, "findings:read", NOW + timedelta(hours=1), None)


@pytest.mark.parametrize(
    ("user", "action", "grant", "now", "allowed"),
    [
        (BOB, "read", GRANT, NOW, True),
        (BOB, "read", GRANT, NOW + timedelta(minutes=59), True),
        (BOB, "read", GRANT, NOW + timedelta(hours=1), False),  # expiry instant is exclusive
        (BOB, "read", GRANT, NOW + timedelta(days=30), False),
        (BOB, "read", replace(GRANT, revoked_at=NOW), NOW, False),
        (uuid4(), "read", GRANT, NOW, False),  # wrong principal
        (BOB, "write", GRANT, NOW, False),  # no write permit exists
        (BOB, "read", replace(GRANT, scope="documents:read"), NOW, False),  # scope mismatch
    ],
)
def test_decision_table(user, action, grant, now, allowed) -> None:  # type: ignore[no-untyped-def]
    assert CedarShareAuthorizer().is_permitted(user, action, grant, now) is allowed
