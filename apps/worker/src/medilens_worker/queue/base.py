"""Queue consumer abstraction. Bodies carry IDs only, never PHI."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Message:
    receipt: str  # opaque handle used for ack / visibility
    body: str  # raw JSON, parsed by the runner


class Queue(Protocol):
    def receive(self) -> Message | None: ...
    def send(self, body: str, delay_seconds: int = 0) -> None: ...
    def ack(self, msg: Message) -> None: ...
    def extend_visibility(self, msg: Message, seconds: int) -> None: ...
    def send_dlq(self, msg: Message, reason: str) -> None: ...
