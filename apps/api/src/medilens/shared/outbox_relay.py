"""Outbox relay: publishes unpublished clinical.outbox rows as worker SQS jobs (at-least-once).

Run: python -m medilens.shared.outbox_relay  (env DATABASE_URL, WORKER_QUEUE_URL, optional
AWS_ENDPOINT_URL).
"""

import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from sqlalchemy import Engine, text

log = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2.0
BATCH_SIZE = 20


def _to_job(event_type: str, p: dict[str, Any]) -> dict[str, Any] | None:
    if event_type == "DocumentUploaded":
        return {
            "type": "document.validate",
            "documentId": p["document_id"],
            "storageKey": p["storage_key"],
            "mime": p["mime"],
            "attempt": 1,
        }
    return None


def relay_once(engine: Engine, publish: Callable[[str], None], batch: int = BATCH_SIZE) -> int:
    """Publish up to `batch` rows; a publish error rolls back, leaving that row unpublished."""
    sent = 0
    with engine.begin() as c:
        rows = c.execute(
            text(
                "SELECT id, event_type, payload FROM clinical.outbox WHERE published_at IS NULL "
                "ORDER BY id LIMIT :n FOR UPDATE SKIP LOCKED"
            ),
            {"n": batch},
        ).all()
        for row_id, event_type, payload in rows:
            job = _to_job(event_type, payload)
            if job is None:
                log.warning("outbox: skipping unknown event_type=%s", event_type)
                continue
            publish(json.dumps(job, separators=(",", ":")))
            c.execute(
                text("UPDATE clinical.outbox SET published_at = now() WHERE id = :i"), {"i": row_id}
            )
            sent += 1
    return sent


def sqs_publisher(queue_url: str, client: Any | None = None) -> Callable[[str], None]:
    if client is None:
        import boto3

        client = boto3.client("sqs", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
    return lambda body: client.send_message(QueueUrl=queue_url, MessageBody=body)


def main() -> None:
    from medilens.core.db import make_engine

    engine = make_engine(os.environ["DATABASE_URL"])
    publish = sqs_publisher(os.environ["WORKER_QUEUE_URL"])
    while True:
        try:
            if relay_once(engine, publish):
                continue  # drain backlog before sleeping
        except Exception:
            log.exception("outbox relay iteration failed")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
