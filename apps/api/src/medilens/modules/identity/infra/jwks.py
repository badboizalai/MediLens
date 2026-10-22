"""JWKS fetch with TTL cache and rotation: an unknown `kid` forces one refresh (rate limited)."""

import json
import threading
import time
import urllib.request
from collections.abc import Callable
from typing import Any

import jwt


def fetch_jwks(url: str) -> dict[str, Any]:
    if not url.startswith(("https://", "http://")):
        raise ValueError("jwks url must be http(s)")
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 - scheme checked above
        return json.load(resp)  # type: ignore[no-any-return]


class CachedJwks:
    def __init__(
        self,
        url: str,
        ttl: int = 3600,
        min_refresh: int = 30,
        fetch: Callable[[str], dict[str, Any]] = fetch_jwks,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._url, self._ttl, self._min_refresh = url, ttl, min_refresh
        self._fetch, self._clock = fetch, clock
        self._keys: dict[str, Any] = {}
        self._fetched_at: float | None = None
        self._lock = threading.Lock()

    def _refresh(self) -> None:
        data = self._fetch(self._url)
        self._keys = {
            k["kid"]: jwt.PyJWK(k).key
            for k in data.get("keys", [])
            if k.get("kid") and k.get("use", "sig") == "sig"
        }
        self._fetched_at = self._clock()

    def get_key(self, kid: str) -> Any:
        with self._lock:
            age = None if self._fetched_at is None else self._clock() - self._fetched_at
            if age is None or age > self._ttl:
                self._refresh()
            elif kid not in self._keys and age >= self._min_refresh:
                self._refresh()  # key rotation
            if kid not in self._keys:
                raise KeyError(kid)
            return self._keys[kid]
