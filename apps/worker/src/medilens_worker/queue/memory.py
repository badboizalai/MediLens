"""In-memory queue for local runs and tests."""

import itertools
import time
from collections.abc import Callable

from medilens_worker.queue.base import Message


class InMemoryQueue:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._ids = itertools.count(1)
        self._items: dict[str, list] = {}  # receipt -> [body, visible_at]
        self.dlq: list[tuple[str, str]] = []  # (body, reason)
        self.extensions: list[tuple[str, int]] = []
        self.sent_delays: list[int] = []

    def send(self, body: str, delay_seconds: int = 0) -> None:
        self.sent_delays.append(delay_seconds)
        self._items[f"r{next(self._ids)}"] = [body, self._clock() + delay_seconds]

    def receive(self) -> Message | None:
        now = self._clock()
        for receipt, (body, visible_at) in self._items.items():
            if visible_at <= now:
                self._items[receipt][1] = now + 30  # default visibility timeout
                return Message(receipt, body)
        return None

    def ack(self, msg: Message) -> None:
        self._items.pop(msg.receipt, None)

    def extend_visibility(self, msg: Message, seconds: int) -> None:
        self.extensions.append((msg.receipt, seconds))
        if msg.receipt in self._items:
            self._items[msg.receipt][1] = self._clock() + seconds

    def send_dlq(self, msg: Message, reason: str) -> None:
        self.dlq.append((msg.body, reason))
        self.ack(msg)

    def make_all_visible(self) -> None:
        """Test helper: skip backoff waits."""
        for item in self._items.values():
            item[1] = 0
