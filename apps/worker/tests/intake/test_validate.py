import boto3
import pytest
from medilens_worker.intake.validate import MAX_PDF_PAGES, ScanPending, validate_upload
from medilens_worker.ocr.service import InMemoryPageStore
from medilens_worker.pipeline.state import NonRetryable
from moto import mock_aws

KEY = "quarantine/p1/d1"
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20


def pdf(pages: int = 1, extra: bytes = b"") -> bytes:
    return b"%PDF-1.4\n" + b"<< /Type /Page >>\n" * pages + b"<< /Type /Pages >>\n" + extra


def msg(mime: str = "image/png", **kw):
    return {"type": "document.validate", "documentId": "d1", "storageKey": KEY, "mime": mime, **kw}


def mem(data: bytes, scan: str | None = None) -> InMemoryPageStore:
    s = InMemoryPageStore()
    s.uploads[KEY] = data
    if scan:
        s.scan[KEY] = scan
    return s


def reason(m, store, **kw) -> str:
    with pytest.raises(NonRetryable) as e:
        validate_upload("d1", m, store, **kw)
    return e.value.reason


@pytest.mark.parametrize(
    "m", [{}, {"storageKey": 5}, {"storageKey": "other/x"}, {"storageKey": "quarantine/../x"}]
)
def test_raw_key_missing(m):
    assert reason(m, InMemoryPageStore()) == "raw_key_missing"


PDF = "application/pdf"


@pytest.mark.parametrize(
    ("data", "m", "want"),
    [
        (b"x" * 40, msg(), "unsupported_type"),
        (PNG, msg(PDF), "mime_mismatch"),
        (pdf(MAX_PDF_PAGES + 1), msg(PDF), "too_many_pages"),
        (pdf(extra=b"/JavaScript (x)"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/OpenAction << /S /JS >>"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/EmbeddedFile"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/Launch"), msg(PDF), "pdf_active_content"),
    ],
)
def test_rejections(data, m, want):
    assert reason(m, mem(data)) == want


def test_too_large(monkeypatch):
    monkeypatch.setattr("medilens_worker.intake.validate.MAX_BYTES", 10)
    assert reason(msg(), mem(PNG)) == "file_too_large"


def test_happy_path_promotes_and_retry_keeps_key():
    s = mem(pdf(MAX_PDF_PAGES))
    m = msg(PDF, attempt=1)
    validate_upload("d1", {**m, "attempt": 2}, s)  # retry re-sends the same dict
    assert s.raw_pages("d1") == [pdf(MAX_PDF_PAGES)]


def test_malware_scan_paths():
    assert reason(msg(), mem(PNG, "THREATS_FOUND"), require_scan=True) == "malware_detected"
    with pytest.raises(ScanPending):
        validate_upload("d1", msg(), mem(PNG), require_scan=True)
    s = mem(PNG, "NO_THREATS_FOUND")
    validate_upload("d1", msg(), s, require_scan=True)
    assert s.raw_pages("d1") == [PNG]
    validate_upload("d1", msg(), mem(PNG))  # off by default


def test_scan_env(monkeypatch):
    monkeypatch.setenv("WORKER_REQUIRE_MALWARE_SCAN", "true")
    with pytest.raises(ScanPending):
        validate_upload("d1", msg(), mem(PNG))


def test_s3_promote_and_scan_tag(monkeypatch):
    from medilens_worker.storage.s3 import S3PageStore

    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(k, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        c = boto3.client("s3")
        for b in ("raw", "processed"):
            c.create_bucket(Bucket=b)
        tag = "GuardDutyMalwareScanStatus=NO_THREATS_FOUND"
        c.put_object(Bucket="raw", Key=KEY, Body=PNG, Tagging=tag)
        s = S3PageStore("processed", raw_bucket="raw")
        validate_upload("d1", msg(), s, require_scan=True)
        assert s.raw_pages("d1") == [PNG]
        got = c.get_object(Bucket="processed", Key="raw/d1/0000")
        assert got["ServerSideEncryption"] == "AES256"
        c.put_object(Bucket="raw", Key=KEY, Body=PNG)
        with pytest.raises(ScanPending):
            validate_upload("d1", msg(), s, require_scan=True)
