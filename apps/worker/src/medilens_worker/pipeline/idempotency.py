"""Per-message idempotency: key = document_id + step + attempt."""

from typing import Protocol


def dedup_key(document_id: str, step: str, attempt: int) -> str:
    return f"{document_id}:{step}:{attempt}"


class IdempotencyStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str) -> None: ...


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def seen(self, key: str) -> bool:
        return key in self._keys

    def mark(self, key: str) -> None:
        self._keys.add(key)
