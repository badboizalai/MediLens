"""Per-message idempotency: key = document_id + step + attempt, held as a lease."""

import time
from collections.abc import Callable
from typing import Protocol

LEASE_SECONDS = 900  # keep >= the queue visibility timeout, else a live worker can be pre-empted


def dedup_key(document_id: str, step: str, attempt: int) -> str:
    return f"{document_id}:{step}:{attempt}"


class IdempotencyStore(Protocol):
    def claim(self, key: str) -> bool:
        """True for exactly one caller: no row yet, or an unfinished lease that expired."""
        ...

    def seen(self, key: str) -> bool:
        """True once the key is marked done."""
        ...

    def mark(self, key: str) -> None:
        """Mark done: never claimable again."""
        ...

    def release(self, key: str) -> None:
        """Drop an unfinished lease after a handled failure."""
        ...


class InMemoryIdempotencyStore:
    def __init__(
        self, lease_seconds: float = LEASE_SECONDS, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._rows: dict[str, tuple[float, bool]] = {}  # key -> (claimed_at, done)
        self._lease, self._clock = lease_seconds, clock

    def claim(self, key: str) -> bool:
        row = self._rows.get(key)
        now = self._clock()
        if row is not None and (row[1] or now - row[0] < self._lease):
            return False
        self._rows[key] = (now, False)
        return True

    def seen(self, key: str) -> bool:
        return self._rows.get(key, (0.0, False))[1]

    def mark(self, key: str) -> None:
        self._rows[key] = (self._clock(), True)

    def release(self, key: str) -> None:
        if not self.seen(key):
            self._rows.pop(key, None)
