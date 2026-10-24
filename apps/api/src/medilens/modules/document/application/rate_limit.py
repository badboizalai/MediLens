"""Per-user upload rate limit, daily quota and SSE stream cap (SEC-AP-08, AC-07).

Keys are the authenticated subject, never an IP. shortcut: state is per process, so N API tasks
allow N x the limit; use Redis INCR+EXPIRE (settings.redis_url) behind this port when scaled out.
"""

import math
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Protocol

from medilens.core.errors import AppError

MINUTE = 60.0
DAY = 86400.0


class TooManyRequests(AppError):
    status = 429
    code = "MEDILENS-429"
    slug = "rate-limited"
    title = "Too many requests"

    def __init__(self, detail: str, retry_after: float) -> None:
        super().__init__(detail)
        self.headers = {"Retry-After": str(max(1, math.ceil(retry_after)))}


class UsageLimiter(Protocol):
    def hit(self, key: str, limit: int, window: float) -> float | None:
        """Records one use; returns seconds to wait when over the limit (nothing recorded)."""

    def acquire(self, key: str, limit: int) -> bool: ...

    def release(self, key: str) -> None: ...


class InMemoryLimiter:
    def __init__(self, now: Callable[[], float] = time.monotonic) -> None:
        self._now = now
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._open: dict[str, int] = defaultdict(int)

    def hit(self, key: str, limit: int, window: float) -> float | None:
        with self._lock:
            now, q = self._now(), self._hits[key]
            while q and now - q[0] >= window:
                q.popleft()
            if len(q) >= limit:
                return q[0] + window - now
            q.append(now)
            return None

    def acquire(self, key: str, limit: int) -> bool:
        with self._lock:
            if self._open[key] >= limit:
                return False
            self._open[key] += 1
            return True

    def release(self, key: str) -> None:
        with self._lock:
            self._open[key] = max(0, self._open[key] - 1)


def check_upload_allowed(
    limiter: UsageLimiter, subject: str, per_minute: int, per_day: int
) -> None:
    wait = limiter.hit(f"upload-rate:{subject}", per_minute, MINUTE)
    if wait is not None:
        raise TooManyRequests("Too many upload requests; slow down.", wait)
    wait = limiter.hit(f"upload-day:{subject}", per_day, DAY)
    if wait is not None:
        raise TooManyRequests("Daily upload quota reached; try again later.", wait)
