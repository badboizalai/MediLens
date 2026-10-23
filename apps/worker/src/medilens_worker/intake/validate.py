"""`document.validate`: check the raw upload named in the job message, then promote it.

Failure reasons are stable codes; content is never logged.
"""

import os
import re
from collections.abc import Mapping

from medilens_worker.ocr.service import PageStore
from medilens_worker.pipeline.state import NonRetryable, RetryLater

MAX_BYTES = 20 * 1024 * 1024  # same limit as the API (BR-010)
MAX_PDF_PAGES = 50  # assumption: no documented limit; a record longer than this is out of scope
_HEIC_BRANDS = {b"heic", b"heix", b"heim", b"heis", b"mif1", b"msf1"}  # copied from the API sniff
_ACTIVE = re.compile(rb"/(JavaScript|JS|Launch|EmbeddedFile)(?![A-Za-z])")
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
        if _ACTIVE.search(data):
            raise Rejected("pdf_active_content")
        if len(_PAGE.findall(data)) > MAX_PDF_PAGES:
            raise Rejected("too_many_pages")
    store.save_raw(document_id, data)
