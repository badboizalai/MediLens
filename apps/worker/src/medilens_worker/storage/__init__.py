"""Pick persistent stores from env; in-memory is the local default."""

import os

from medilens_worker.ocr import service as ocr_service
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.state import StatusRepo


def build_stores():  # noqa: ANN201 - returns (status repo, idempotency store), duck-typed
    if bucket := os.environ.get("WORKER_PAGES_BUCKET"):
        from medilens_worker.storage.s3 import S3PageStore  # noqa: PLC0415

        raw = os.environ.get("WORKER_RAW_BUCKET")
        ocr_service.configure(store=S3PageStore(bucket, raw, os.environ.get("AWS_ENDPOINT_URL")))
    if url := os.environ.get("WORKER_DATABASE_URL"):
        from medilens_worker.storage.postgres import (  # noqa: PLC0415
            PgIdempotencyStore,
            PgStatusRepo,
        )

        return PgStatusRepo(url), PgIdempotencyStore(url)
    return StatusRepo(), InMemoryIdempotencyStore()
