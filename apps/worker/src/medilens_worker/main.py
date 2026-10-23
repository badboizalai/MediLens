"""Worker entrypoint: poll the queue and process messages."""

import logging
import os
from collections.abc import Mapping

from medilens_worker.extraction import deps as extract_deps
from medilens_worker.extraction.service import HttpGatewayClient
from medilens_worker.ocr import service as ocr_service
from medilens_worker.pipeline.runner import handle
from medilens_worker.queue.base import Queue
from medilens_worker.queue.events import EventSink, InMemoryEventSink, SqsEventSink
from medilens_worker.storage import build_stores
from medilens_worker.storage.results import InMemoryResultStore, S3ResultStore


def build_queue() -> Queue:
    url = os.environ.get("WORKER_QUEUE_URL")
    if not url:
        from medilens_worker.queue.memory import InMemoryQueue

        return InMemoryQueue()
    from medilens_worker.queue.sqs import SqsQueue

    return SqsQueue(url, os.environ["WORKER_DLQ_URL"], os.environ.get("AWS_ENDPOINT_URL"))


def build_events() -> EventSink:
    url = os.environ.get("API_EVENTS_QUEUE_URL")
    if not url:
        return InMemoryEventSink()  # local: events are dropped with the process
    return SqsEventSink(url, os.environ.get("AWS_ENDPOINT_URL"))


def build_extract_deps(
    env: Mapping[str, str] = os.environ, events: EventSink | None = None
) -> extract_deps.ExtractDeps:
    local = env.get("ENV") == "local"  # unset ENV counts as non-local
    url = env.get("AI_GATEWAY_URL") or ("http://localhost:8001" if local else "")
    secret = env.get("AI_GATEWAY_SERVICE_SECRET") or ("local-dev-secret" if local else "")
    tenant = env.get("WORKER_TENANT_ID") or ("local" if local else "")
    results_bucket = env.get("EXTRACTION_RESULTS_BUCKET", "")
    missing = [
        k
        for k, v in (
            ("EXTRACTION_RESULTS_BUCKET", results_bucket or local),
            ("AI_GATEWAY_URL", url),
            ("AI_GATEWAY_SERVICE_SECRET", secret),
            ("WORKER_TENANT_ID", tenant),
        )
        if not v
    ]
    if missing:
        raise RuntimeError(f"missing required env: {', '.join(missing)}")
    results = (
        S3ResultStore(results_bucket, env.get("AWS_ENDPOINT_URL"), env.get("PHI_KMS_KEY_ID"))
        if results_bucket
        else InMemoryResultStore()  # local only
    )

    def load_pages(doc: str) -> list[str]:
        pages = [p.text for p in ocr_service.get_store().ocr_pages(doc)]
        if not pages:
            raise LookupError("no_ocr_pages")  # never extract from nothing
        return pages

    return extract_deps.ExtractDeps(
        load_pages=load_pages,
        client=HttpGatewayClient(url, tenant, secret),
        save_run=results.save,
        load_run=results.latest,
        emit=events or InMemoryEventSink(),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    events = build_events()
    extract_deps.configure(build_extract_deps(events=events))
    queue = build_queue()
    statuses, store = build_stores()
    while True:
        msg = queue.receive()
        if msg is not None:
            handle(queue, msg, statuses, store, events=events)
        elif not os.environ.get("WORKER_QUEUE_URL"):
            return  # in-memory queue never fills by itself


if __name__ == "__main__":
    main()
