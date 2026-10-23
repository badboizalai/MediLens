"""Page and result writes use SSE-KMS with the PHI CMK, never AES256."""

import pytest
from medilens_worker.extraction.service import ExtractionRun
from medilens_worker.storage.results import S3ResultStore
from medilens_worker.storage.s3 import S3PageStore

KEY = "arn:aws:kms:ap-southeast-1:111111111111:key/phi"


class Spy:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def put_object(self, **kw) -> None:
        self.calls.append(kw)


def run() -> ExtractionRun:
    return ExtractionRun("d", "dental", "m", "p", 0.0, 1.0, {}, [], False, "r", "v")


def pages(kms: str | None) -> tuple[S3PageStore, Spy]:
    s = S3PageStore("b", kms_key_id=kms)
    s._c = spy = Spy()
    return s, spy


def results(kms: str | None) -> tuple[S3ResultStore, Spy]:
    s = S3ResultStore("b", kms_key_id=kms)
    s._c = spy = Spy()
    return s, spy


@pytest.mark.parametrize("make", [pages, results])
def test_key_id_is_sent_when_configured(make) -> None:
    s, spy = make(KEY)
    s.save_raw("d", b"x") if make is pages else s.save(run())
    got = spy.calls[0]
    assert got["ServerSideEncryption"] == "aws:kms" and got["SSEKMSKeyId"] == KEY


@pytest.mark.parametrize("make", [pages, results])
def test_unset_key_falls_back_to_bucket_default_never_aes256(make) -> None:
    s, spy = make(None)
    s.save_raw("d", b"x") if make is pages else s.save(run())
    got = spy.calls[0]
    assert got["ServerSideEncryption"] == "aws:kms" and "SSEKMSKeyId" not in got
