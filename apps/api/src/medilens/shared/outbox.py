"""Transactional outbox writer. Events join the caller's DB transaction; the relay publishes them."""

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class SqlOutbox:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event_type: str, payload: dict[str, Any]) -> None:
        """Payloads carry ids only, never PHI."""
        self._session.execute(
            text(
                "INSERT INTO clinical.outbox (event_type, payload) VALUES (:t, CAST(:p AS jsonb))"
            ),
            {"t": event_type, "p": json.dumps(payload)},
        )
