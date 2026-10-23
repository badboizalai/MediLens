"""api-events consumer: applies worker `document.status_changed` to the API (ADR-0005).

Run: python -m medilens.shared.api_events_consumer  (env DATABASE_URL, API_EVENTS_QUEUE_URL,
optional AWS_ENDPOINT_URL). A message is deleted only after its transaction commits; an invalid
one is left on the queue so the redrive policy moves it to the DLQ. `extraction.completed` ingest
is follow-up S6-T53d2 (until then it is rejected as `unsupported_event`).
"""

import json
import logging
import os
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.orm import Session, sessionmaker

from medilens.modules.document.application.service import StatusService
from medilens.modules.document.infra.sql_repository import SqlDocumentRepository

log = logging.getLogger(__name__)


class InvalidEvent(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class StatusChanged(BaseModel):
    """Mirrors docs/architecture/contracts/document-status-changed.schema.json (v1)."""

    model_config = ConfigDict(extra="forbid")
    schemaVersion: Literal[1]  # noqa: N815
    event: Literal["document.status_changed"]
    documentId: UUID  # noqa: N815
    status: Literal[
        "uploaded",
        "validated",
        "preprocessed",
        "classified",
        "ocr_done",
        "extracted",
        "needs_review",
        "confirmed",
        "needs_retake",
        "failed",
    ]
    reason: str | None = Field(default=None, pattern=r"^[a-z0-9_:]+$", max_length=64)


def parse(body: str) -> StatusChanged:
    try:
        data: Any = json.loads(body)
    except ValueError:
        raise InvalidEvent("bad_json") from None
    if not isinstance(data, dict):
        raise InvalidEvent("bad_json")
    if data.get("event") != "document.status_changed":
        raise InvalidEvent("unsupported_event")
    try:
        return StatusChanged.model_validate(data)
    except ValidationError:
        raise InvalidEvent("schema_violation") from None


def handle(body: str, factory: sessionmaker[Session]) -> str:
    """Parse and apply one message in one transaction. Raises InvalidEvent; returns the outcome."""
    ev = parse(body)
    with factory.begin() as session:
        outcome = StatusService(SqlDocumentRepository(session)).apply(ev.documentId, ev.status)
    if outcome == "unknown":
        log.warning("api-events: unknown document id=%s", ev.documentId)  # id only, no payload
    return outcome


def consume_once(client: Any, queue_url: str, factory: sessionmaker[Session]) -> int:
    """Long-poll one batch; returns messages deleted."""
    resp = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=10)
    deleted = 0
    for m in resp.get("Messages", []):
        try:
            handle(m["Body"], factory)
        except InvalidEvent as e:
            log.error("api-events: invalid message id=%s reason=%s", m["MessageId"], e.reason)
            continue  # left for the DLQ
        except Exception:
            log.exception("api-events: apply failed id=%s", m["MessageId"])
            continue  # transaction rolled back; SQS redelivers
        client.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])
        deleted += 1
    return deleted


def main() -> None:
    import boto3

    from medilens.core.db import make_engine, make_session_factory

    factory = make_session_factory(make_engine(os.environ["DATABASE_URL"]))
    client = boto3.client("sqs", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
    queue_url = os.environ["API_EVENTS_QUEUE_URL"]
    while True:
        consume_once(client, queue_url, factory)


if __name__ == "__main__":
    main()
