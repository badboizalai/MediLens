"""`document.validate`: check the raw upload named in the job message, then promote it.

Failure reasons are stable codes; content is never logged.
"""

import os
import re
from collections.abc import Mapping

from medilens_worker.intake.pixels import MAX_IMAGE_PIXELS, declared_pixels
from medilens_worker.ocr.service import PageStore
from medilens_worker.pipeline.state import NonRetryable, RetryLater

MAX_BYTES = 20 * 1024 * 1024  # same limit as the API (BR-010)
MAX_PDF_PAGES = 50  # assumption: no documented limit; a record longer than this is out of scope
_HEIC_BRANDS = {b"heic", b"heix", b"heim", b"heis", b"mif1", b"msf1"}  # copied from the API sniff
_ACTIVE = re.compile(
    rb"/\s*(JavaScript|JS|Launch|EmbeddedFile|OpenAction|AA|SubmitForm|XFA|RichMedia)(?![A-Za-z])"
)
# bytes allowed after the last %%EOF (EOL/padding); more is appended data
PDF_TRAILING_TOLERANCE = 16
# Polyglot markers anywhere in the raw bytes. Trade-off: a legit PDF whose compressed stream
# happens to contain one of these (4-byte `PK\x03\x04` ~ 2^-32 per offset) is rejected; accepted.
_POLYGLOT = re.compile(rb"PK\x03\x04|<html|<script|<!doctype\s+html", re.I)
_NAME_HEX = re.compile(rb"#([0-9A-Fa-f]{2})")
_UNINSPECTABLE = re.compile(rb"/\s*(ObjStm|Encrypt)(?![A-Za-z])")
# shortcut: byte-level count misses pages inside compressed object streams; use a PDF parser then
_PAGE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")


class ScanPending(RetryLater):
    """Malware scan verdict not available yet: retryable."""


class Rejected(NonRetryable):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sniff_mime(head: bytes) -> str | None:
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head[4:8] == b"ftyp" and head[8:12] in _HEIC_BRANDS:
        return "image/heic"
    return None


def validate_upload(
    document_id: str,
    message: Mapping[str, object],
    store: PageStore,
    require_scan: bool | None = None,
) -> None:
    key = message.get("storageKey")
    if not isinstance(key, str) or not key.startswith("quarantine/") or ".." in key:
        raise Rejected("raw_key_missing")
    if require_scan is None:
        require_scan = os.environ.get("WORKER_REQUIRE_MALWARE_SCAN") == "true"

    size, scan = store.upload_info(key)
    if size > MAX_BYTES:
        raise Rejected("file_too_large")
    if require_scan:
        if scan == "THREATS_FOUND":
            raise Rejected("malware_detected")
        if scan != "NO_THREATS_FOUND":
            raise ScanPending("malware_scan_pending")
    data = store.read_upload(key)
    real = sniff_mime(data[:12])
    if real is None:
        raise Rejected("unsupported_type")
    if real != message.get("mime"):
        raise Rejected("mime_mismatch")
    if real == "application/pdf":
        _check_pdf(data)
    elif real == "image/heic":
        pass  # shortcut: no HEIC decoder in the worker, so no re-encode; add pillow-heif then
    else:
        data = _reencode_png(data)
    store.save_raw(document_id, data)


def _check_pdf(data: bytes) -> None:
    # `/Java#53cript` is the same name as `/JavaScript`: decode #xx before matching
    text = _NAME_HEX.sub(lambda m: bytes([int(m[1], 16)]), data)
    if b"%%EOF" not in text[-1024:] or not (b"startxref" in text or b"/Root" in text):
        raise Rejected("pdf_malformed")  # e.g. a `%PDF-` header on an HTML body
    # shortcut: object streams and encryption hide objects from a byte scan, so reject them;
    # upgrade: parse in a sandbox (S6-T58-F4b) and allow them
    if len(data) - (data.rfind(b"%%EOF") + 5) > PDF_TRAILING_TOLERANCE:
        raise Rejected("trailing_data")
    if _POLYGLOT.search(data):
        raise Rejected("pdf_polyglot")
    if _UNINSPECTABLE.search(text):
        raise Rejected("pdf_uninspectable")
    if _ACTIVE.search(text):
        raise Rejected("pdf_active_content")
    if len(_PAGE.findall(text)) > MAX_PDF_PAGES:
        raise Rejected("too_many_pages")


def _reencode_png(data: bytes) -> bytes:
    """Decode and re-encode so appended payloads (polyglots) and EXIF are dropped."""
    px = declared_pixels(data)  # header check first: never decode a decompression bomb
    if px is None:
        raise Rejected("unsupported_type")
    if px > MAX_IMAGE_PIXELS:
        raise Rejected("image_too_large")
    import cv2  # noqa: PLC0415  (ocr extra; imported lazily to keep base installs light)
    import numpy as np  # noqa: PLC0415

    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise Rejected("unsupported_type")
    return cv2.imencode(".png", img)[1].tobytes()
