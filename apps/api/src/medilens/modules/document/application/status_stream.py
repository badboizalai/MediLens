import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass

import anyio
from anyio import to_thread

POLL_SECONDS = 1.0  # D53: changes reach the client in < 2 s
HEARTBEAT_SECONDS = 15.0
MAX_STREAM_SECONDS = 300.0  # client reconnects; bounds one DB poller per open stream
# Pipeline end states (state machine, migration 0004): nothing changes until the user acts.
TERMINAL_STATUSES = frozenset({"rejected", "needs_retake", "failed", "needs_review", "confirmed"})


@dataclass(frozen=True)
class Clock:
    sleep: Callable[[float], Awaitable[None]] = anyio.sleep
    monotonic: Callable[[], float] = time.monotonic


async def watch_status(poll: Callable[[], str | None], clock: Clock) -> AsyncIterator[str | None]:
    """Yields the status on first read and on every change, None as a heartbeat; ends on a
    terminal status, when the document disappears, or after MAX_STREAM_SECONDS.
    Only the (blocking) poll uses a worker thread; waiting is an awaited sleep, so idle streams
    hold no thread."""
    start = last_sent = clock.monotonic()
    current: str | None = None
    while True:
        status = await to_thread.run_sync(poll)
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
        await clock.sleep(POLL_SECONDS)
