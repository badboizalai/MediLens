import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass

POLL_SECONDS = 1.0  # D53: changes reach the client in < 2 s
HEARTBEAT_SECONDS = 15.0
MAX_STREAM_SECONDS = 300.0  # client reconnects; bounds one DB poller per open stream
# Pipeline end states (state machine, migration 0004): nothing changes until the user acts.
TERMINAL_STATUSES = frozenset({"rejected", "needs_retake", "failed", "needs_review", "confirmed"})


@dataclass(frozen=True)
class Clock:
    sleep: Callable[[float], None] = time.sleep
    monotonic: Callable[[], float] = time.monotonic


def watch_status(poll: Callable[[], str | None], clock: Clock) -> Iterator[str | None]:
    """Yields the status on first read and on every change, None as a heartbeat; ends on a
    terminal status, when the document disappears, or after MAX_STREAM_SECONDS."""
    start = last_sent = clock.monotonic()
    current: str | None = None
    while True:
        status = poll()
        if status is None:
            return
        now = clock.monotonic()
        if status != current:
            current, last_sent = status, now
            yield status
            if status in TERMINAL_STATUSES:
                return
        elif now - last_sent >= HEARTBEAT_SECONDS:
            last_sent = now
            yield None
        if now - start >= MAX_STREAM_SECONDS:
            return
        clock.sleep(POLL_SECONDS)
