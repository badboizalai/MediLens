"""Same contract for in-memory and persistent implementations."""

import uuid
from concurrent.futures import ThreadPoolExecutor

import boto3
import pytest
from medilens_worker.ocr.service import InMemoryPageStore
from medilens_worker.ocr.types import Metrics, OcrBox, OcrPage, PreprocessedPage, RetakeReason
from medilens_worker.pipeline.idempotency import InMemoryIdempotencyStore
from medilens_worker.pipeline.state import DocStatus, InvalidTransition, StatusRepo
from moto import mock_aws


@pytest.fixture(params=["memory", "postgres"])
def statuses(request: pytest.FixtureRequest):
    if request.param == "memory":
        return StatusRepo()
    from medilens_worker.storage.postgres import PgStatusRepo

    return PgStatusRepo(request.getfixturevalue("pg_url"))


@pytest.fixture(params=["memory", "postgres"])
def idem(request: pytest.FixtureRequest):
    if request.param == "memory":
        return InMemoryIdempotencyStore()
    from medilens_worker.storage.postgres import PgIdempotencyStore

    return PgIdempotencyStore(request.getfixturevalue("pg_url"))


@pytest.fixture(params=["memory", "s3"])
def pages(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    if request.param == "memory":
        yield InMemoryPageStore()
        return
    from medilens_worker.storage.s3 import S3PageStore

    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(k, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        boto3.client("s3").create_bucket(Bucket="processed")
        yield S3PageStore("processed")


def test_status_default_and_guarded_transitions(statuses) -> None:
    d = str(uuid.uuid4())
    assert statuses.get(d) == DocStatus.UPLOADED
    statuses.set(d, DocStatus.VALIDATED)
    assert statuses.get(d) == DocStatus.VALIDATED
    with pytest.raises(InvalidTransition):
        statuses.set(d, DocStatus.OCR_DONE)
    assert statuses.get(d) == DocStatus.VALIDATED


def test_status_reason(statuses) -> None:
    d = str(uuid.uuid4())
    statuses.set(d, DocStatus.FAILED)
    statuses.reasons[d] = "boom"
    assert statuses.reasons[d] == "boom"


def test_idempotency_mark_seen(idem) -> None:
    k = f"{uuid.uuid4()}:ocr:1"
    assert not idem.seen(k)
    idem.mark(k)
    assert idem.seen(k)


def test_postgres_claim_is_atomic(pg_url: str) -> None:
    from medilens_worker.storage.postgres import PgIdempotencyStore

    s = PgIdempotencyStore(pg_url)
    k = f"{uuid.uuid4()}:ocr:1"
    with ThreadPoolExecutor(8) as ex:
        wins = list(ex.map(lambda _: s.claim(k), range(8)))
    assert wins.count(True) == 1


def test_pages_roundtrip(pages) -> None:
    d = str(uuid.uuid4())
    m = Metrics(blur=100.0, brightness=120.0, ink_ratio=0.1)
    pages.save_preprocessed(
        d, [PreprocessedPage(2, b"b", 0.8, m), PreprocessedPage(1, b"a", 0.9, m)]
    )
    got = sorted(pages.preprocessed(d), key=lambda p: p.page)
    assert [(p.page, p.image, p.metrics) for p in got] == [(1, b"a", m), (2, b"b", m)]
    ocr = [OcrPage(1, "xin chao", [OcrBox("xin chao", 0, 0, 5, 5, 0.9)], 0.9)]
    pages.save_ocr(d, ocr)
    pages.save_retake(d, 1, RetakeReason.BLURRY)
    # InMemoryPageStore gains ocr_pages in BUG-03; until it merges read its dict directly.
    read = pages.ocr_pages if hasattr(pages, "ocr_pages") else pages.ocr.__getitem__
    assert read(d) == ocr


def test_s3_keys_hold_no_text(monkeypatch: pytest.MonkeyPatch) -> None:
    from medilens_worker.storage.s3 import S3PageStore

    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(k, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        c = boto3.client("s3")
        c.create_bucket(Bucket="processed")
        S3PageStore("processed").save_ocr("doc1", [OcrPage(1, "Nguyen Van A", [], 0.5)])
        keys = [o["Key"] for o in c.list_objects_v2(Bucket="processed")["Contents"]]
        assert keys == ["ocr/doc1/0001.json"]
