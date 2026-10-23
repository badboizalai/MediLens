import struct
import zlib
from importlib.util import find_spec

import boto3
import pytest
from medilens_worker.intake.validate import MAX_PDF_PAGES, ScanPending, validate_upload
from medilens_worker.ocr.service import InMemoryPageStore
from medilens_worker.pipeline.state import NonRetryable
from moto import mock_aws

KEY = "quarantine/p1/d1"
# image decode needs the optional `ocr` extra (cv2); without it these tests are skipped
needs_cv2 = pytest.mark.skipif(find_spec("cv2") is None, reason="opencv not installed")


def _chunk(tag: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body))


def make_png() -> bytes:  # 1x1 grey pixel, built with the stdlib
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(b"\x00\x80"))
        + _chunk(b"IEND", b"")
    )


PNG = make_png()
ZIP_TAIL = b"PK\x03\x04" + b"\x00" * 26 + b"payload.txt" + b"PK\x05\x06" + b"\x00" * 18


def pdf(pages: int = 1, extra: bytes = b"") -> bytes:
    return (
        b"%PDF-1.4\n"
        + b"<< /Type /Page >>\n" * pages
        + b"<< /Type /Pages >>\n"
        + extra
        + b"\ntrailer << /Root 1 0 R >>\nstartxref\n0\n%%EOF\n"
    )


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
        (pdf(extra=b"/Java#53cript (x)"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/Open#41ction 1 0 R"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/AA << /O 1 0 R >>"), msg(PDF), "pdf_active_content"),
        (pdf(extra=b"/Type /ObjStm"), msg(PDF), "pdf_uninspectable"),
        (pdf(extra=b"/Type /Obj#53tm"), msg(PDF), "pdf_uninspectable"),
        (pdf(extra=b"/Encrypt 9 0 R"), msg(PDF), "pdf_uninspectable"),
        (b"%PDF-1.7\n<html><script>alert(1)</script></html>\n", msg(PDF), "pdf_malformed"),
        (pdf().replace(b"%%EOF", b""), msg(PDF), "pdf_malformed"),
        (pdf(pages=MAX_PDF_PAGES + 1, extra=b"/Type /Pa#67e"), msg(PDF), "too_many_pages"),
    ],
)
def test_rejections(data, m, want):
    assert reason(m, mem(data)) == want


@needs_cv2
def test_undecodable_image_is_unsupported():
    assert reason(msg(), mem(PNG[:8] + b"0" * 20)) == "unsupported_type"


@needs_cv2
def test_jpeg_zip_polyglot_is_stripped():
    import cv2
    import numpy as np

    jpg = cv2.imencode(".jpg", np.zeros((8, 8, 3), np.uint8))[1].tobytes()
    s = mem(jpg + ZIP_TAIL)
    validate_upload("d1", msg("image/jpeg"), s)
    (out,) = s.raw_pages("d1")
    assert out.startswith(b"\x89PNG") and b"PK\x03\x04" not in out and b"PK\x05\x06" not in out


@needs_cv2
def test_png_with_appended_zip_is_stripped():
    s = mem(PNG + ZIP_TAIL)
    validate_upload("d1", msg(), s)
    assert b"PK\x03\x04" not in s.raw_pages("d1")[0]


def test_heic_passes_through_unchanged():
    data = b"\x00\x00\x00\x18ftypheic" + b"0" * 20
    s = mem(data)
    validate_upload("d1", msg("image/heic"), s)
    assert s.raw_pages("d1") == [data]


def test_too_large(monkeypatch):
    monkeypatch.setattr("medilens_worker.intake.validate.MAX_BYTES", 10)
    assert reason(msg(), mem(PNG)) == "file_too_large"


def test_happy_path_promotes_and_retry_keeps_key():
    s = mem(pdf(MAX_PDF_PAGES))
    m = msg(PDF, attempt=1)
    validate_upload("d1", {**m, "attempt": 2}, s)  # retry re-sends the same dict
    assert s.raw_pages("d1") == [pdf(MAX_PDF_PAGES)]


@needs_cv2
def test_malware_scan_paths():
    assert reason(msg(), mem(PNG, "THREATS_FOUND"), require_scan=True) == "malware_detected"
    with pytest.raises(ScanPending):
        validate_upload("d1", msg(), mem(PNG), require_scan=True)
    s = mem(PNG, "NO_THREATS_FOUND")
    validate_upload("d1", msg(), s, require_scan=True)
    assert s.raw_pages("d1")[0].startswith(b"\x89PNG")
    validate_upload("d1", msg(), mem(PNG))  # off by default


@needs_cv2
def test_scan_env(monkeypatch):
    monkeypatch.setenv("WORKER_REQUIRE_MALWARE_SCAN", "true")
    with pytest.raises(ScanPending):
        validate_upload("d1", msg(), mem(PNG))


@needs_cv2
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
        assert s.raw_pages("d1")[0].startswith(b"\x89PNG")
        got = c.get_object(Bucket="processed", Key="raw/d1/0000")
        assert got["ServerSideEncryption"] == "aws:kms"
        c.put_object(Bucket="raw", Key=KEY, Body=PNG)
        with pytest.raises(ScanPending):
            validate_upload("d1", msg(), s, require_scan=True)


def _png_declaring(w: int, h: int) -> bytes:  # tiny file whose header claims w x h pixels
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    return PNG[:8] + _chunk(b"IHDR", ihdr) + PNG[33:]


def test_huge_declared_dimensions_rejected_before_decode(monkeypatch):
    # no needs_cv2: must be rejected from the header alone, without importing cv2
    monkeypatch.setitem(__import__("sys").modules, "cv2", None)
    assert reason(msg(), mem(_png_declaring(100_000, 100_000))) == "image_too_large"


def test_cap_boundary():
    from medilens_worker.intake.pixels import MAX_IMAGE_PIXELS, within_pixel_cap

    assert within_pixel_cap(_png_declaring(MAX_IMAGE_PIXELS, 1))
    assert not within_pixel_cap(_png_declaring(MAX_IMAGE_PIXELS, 2))
    assert not within_pixel_cap(b"\xff\xd8\xff\xd9")  # no SOF: fails closed


def test_jpeg_header_dims():
    from medilens_worker.intake.pixels import declared_pixels

    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 30000, 40000, 1) + b"\x00" * 3
    assert declared_pixels(b"\xff\xd8" + sof) == 1_200_000_000
    assert declared_pixels(b"\xff\xd8\xff\xff" + sof) == 1_200_000_000  # fill byte before SOF


@needs_cv2
def test_normal_image_still_passes():
    s = mem(PNG)
    validate_upload("d1", msg(), s)
    assert s.raw_pages("d1")
