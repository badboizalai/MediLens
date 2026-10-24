"""Per-user daily token budget (SEC-AI-07). In-memory; use Redis INCRBY with a day-keyed TTL when scaled out."""

from collections.abc import Callable

DAY_S = 86_400


class QuotaExceeded(Exception):
    def __init__(self, retry_after_s: int) -> None:
        super().__init__("daily token quota exceeded")
        self.retry_after_s = retry_after_s


class TokenQuota:
    def __init__(self, daily_tokens: int, wall_clock: Callable[[], float]) -> None:
        self.daily_tokens, self._now = daily_tokens, wall_clock
        self._used: dict[tuple[str, str], tuple[int, int]] = {}  # user -> (day, tokens)

    def _usage(self, user: tuple[str, str]) -> tuple[int, int]:
        day = int(self._now() // DAY_S)  # UTC day; a new day resets usage
        d, used = self._used.get(user, (day, 0))
        return (day, used) if d == day else (day, 0)

    def check(self, user: tuple[str, str]) -> None:
        """Raise before a call when the budget is spent (the last call may overshoot)."""
        day, used = self._usage(user)
        if used >= self.daily_tokens:
            raise QuotaExceeded(int((day + 1) * DAY_S - self._now()) + 1)

    def charge(self, user: tuple[str, str], tokens: int) -> None:
        day, used = self._usage(user)
        self._used[user] = (day, used + tokens)
