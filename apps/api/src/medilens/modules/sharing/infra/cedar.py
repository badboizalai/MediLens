"""Cedar adapter (cedarpy, Apache-2.0, wraps the AWS cedar-policy engine). Policy: share.cedar."""

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import cedarpy

from medilens.modules.sharing.domain.models import Grant

_POLICY = (Path(__file__).resolve().parents[1] / "policies" / "share.cedar").read_text()


def _ref(user_id: UUID) -> dict[str, dict[str, str]]:
    return {"__entity": {"type": "User", "id": str(user_id)}}


class CedarShareAuthorizer:
    def is_permitted(self, user_id: UUID, action: str, grant: Grant, now: datetime) -> bool:
        entities: list[dict[str, Any]] = [
            {"uid": {"type": "User", "id": str(user_id)}, "attrs": {}, "parents": []},
            {
                "uid": {"type": "Share", "id": str(grant.id)},
                "attrs": {
                    "grantee": _ref(grant.grantee_user_id),
                    "scope": grant.scope,
                    "expires_at": int(grant.expires_at.timestamp()),
                    "revoked": grant.revoked_at is not None,
                },
                "parents": [],
            },
        ]
        request = {
            "principal": f'User::"{user_id}"',
            "action": f'Action::"{action}"',
            "resource": f'Share::"{grant.id}"',
            "context": {"now": int(now.timestamp())},
        }
        return bool(cedarpy.is_authorized(request, _POLICY, entities).allowed)
