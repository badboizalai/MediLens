"""Worker entrypoint: poll the queue and process messages."""

import logging
import os

from medilens_worker.pipeline.runner import handle
from medilens_worker.queue.base import Queue
from medilens_worker.storage import build_stores


def build_queue() -> Queue:
    url = os.environ.get("WORKER_QUEUE_URL")
    if not url:
        from medilens_worker.queue.memory import InMemoryQueue

        return InMemoryQueue()
    from medilens_worker.queue.sqs import SqsQueue

    return SqsQueue(url, os.environ["WORKER_DLQ_URL"], os.environ.get("AWS_ENDPOINT_URL"))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    queue = build_queue()
    statuses, store = build_stores()
    while True:
        msg = queue.receive()
        if msg is not None:
            handle(queue, msg, statuses, store)
        elif not os.environ.get("WORKER_QUEUE_URL"):
            return  # in-memory queue never fills by itself


if __name__ == "__main__":
    main()
