"""api-events consumer: applies worker `document.status_changed` to the API (ADR-0005).

Run: python -m medilens.shared.api_events_consumer  (env DATABASE_URL, API_EVENTS_QUEUE_URL,
optional AWS_ENDPOINT_URL). A message is deleted only after its transaction commits; an invalid
one is left on the queue so the redrive policy moves it to the DLQ. `extraction.completed`
(S6-T53d2) reads the result object from S3 (env RESULTS_BUCKET) and ingests it through the definer
function clinical.ingest_extraction; an unknown document is a permanent error (DLQ).
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
from medilens.modules.extraction.infra.ingest import (
    ResultReader,
    S3ResultReader,
    ingest,
    result_key,
)

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


class ExtractionCompleted(BaseModel):
    """Mirrors docs/architecture/contracts/extraction-completed.schema.json (v1)."""

    model_config = ConfigDict(extra="forbid")
    schemaVersion: Literal[1]  # noqa: N815
    event: Literal["extraction.completed"]
    documentId: UUID  # noqa: N815
    runId: UUID  # noqa: N815


class ExtractionFlag(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    reason: str = Field(pattern=r"^[a-z0-9_:]+$")


class ExtractionResult(BaseModel):
    """Mirrors docs/architecture/contracts/extraction-result.schema.json (v1)."""

    model_config = ConfigDict(extra="forbid")
    schemaVersion: Literal[1]  # noqa: N815
    documentId: UUID  # noqa: N815
    runId: UUID  # noqa: N815
    unit: Literal["dental", "cardiology", "oncology"]
    model: str = Field(min_length=1)
    promptVersion: str = Field(min_length=1)  # noqa: N815
    pipelineVersion: str = ""  # noqa: N815
    costUsd: float = Field(ge=0)  # noqa: N815
    confidence: float = Field(ge=0, le=1)
    repaired: bool
    flags: list[ExtractionFlag]
    result: dict[str, Any]


def parse(body: str) -> StatusChanged | ExtractionCompleted:
    try:
        data: Any = json.loads(body)
    except ValueError:
        raise InvalidEvent("bad_json") from None
    if not isinstance(data, dict):
        raise InvalidEvent("bad_json")
    kinds = {"document.status_changed": StatusChanged, "extraction.completed": ExtractionCompleted}
    kind = kinds.get(data.get("event"))  # type: ignore[arg-type]
    if kind is None:
        raise InvalidEvent("unsupported_event")
    try:
        return kind.model_validate(data)
    except ValidationError:
        raise InvalidEvent("schema_violation") from None


def _ingest(ev: ExtractionCompleted, factory: sessionmaker[Session], reader: ResultReader) -> str:
    raw = reader.read(result_key(ev.documentId, ev.runId))  # S3 errors propagate: SQS redelivers
    try:
        doc = ExtractionResult.model_validate_json(raw)
    except ValidationError:
        raise InvalidEvent("result_schema_violation") from None
    if (doc.documentId, doc.runId) != (ev.documentId, ev.runId):
        raise InvalidEvent("result_id_mismatch")
    with factory.begin() as session:
        outcome = ingest(session, json.loads(doc.model_dump_json()))
    if outcome == "unknown":
        log.error("api-events: extraction for unknown document id=%s", ev.documentId)
        raise InvalidEvent("unknown_document")
    return outcome


def handle(body: str, factory: sessionmaker[Session], reader: ResultReader | None = None) -> str:
    """Parse and apply one message in one transaction. Raises InvalidEvent; returns the outcome."""
    ev = parse(body)
    if isinstance(ev, ExtractionCompleted):
        if reader is None:
            raise RuntimeError("extraction.completed needs a result reader (RESULTS_BUCKET)")
        return _ingest(ev, factory, reader)
    with factory.begin() as session:
        outcome = StatusService(SqlDocumentRepository(session)).apply(ev.documentId, ev.status)
    if outcome == "unknown":
        log.warning("api-events: unknown document id=%s", ev.documentId)  # id only, no payload
    return outcome


def consume_once(
    client: Any, queue_url: str, factory: sessionmaker[Session], reader: ResultReader | None = None
) -> int:
    """Long-poll one batch; returns messages deleted."""
    resp = client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=10)
    deleted = 0
    for m in resp.get("Messages", []):
        try:
            handle(m["Body"], factory, reader)
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
    s3 = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
    reader = S3ResultReader(os.environ["RESULTS_BUCKET"], s3)
    while True:
        consume_once(client, queue_url, factory, reader)


if __name__ == "__main__":
    main()
