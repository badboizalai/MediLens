"""Sink for `api-events` messages (ADR-0005 decision 2). Bodies carry ids and enums only."""

import json
from collections.abc import Callable

EventSink = Callable[[dict], None]


class InMemoryEventSink:
    """Local default and test double: keeps events in a list."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def __call__(self, event: dict) -> None:
        self.events.append(event)


class SqsEventSink:
    def __init__(self, queue_url: str, endpoint_url: str | None = None) -> None:
        import boto3  # noqa: PLC0415

        self._c = boto3.client("sqs", endpoint_url=endpoint_url)
        self._url = queue_url

    def __call__(self, event: dict) -> None:
        self._c.send_message(QueueUrl=self._url, MessageBody=json.dumps(event))
