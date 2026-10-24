"""Document upload rules (BR-010, BR-016) and errors. Pure: no framework or storage types."""

from dataclasses import dataclass
from uuid import UUID

from medilens.core.errors import AppError, Forbidden, NotFound

MAX_BYTES = 20 * 1024 * 1024  # BR-010
PRESIGN_TTL_SECONDS = 300  # SEC-DP-05, U-04
STATUS_PENDING = "uploaded-pending"
STATUS_UPLOADED = "uploaded"
STATUS_REJECTED = "rejected"  # BR-010/BR-016: API-only terminal status
EVENT_DOCUMENT_UPLOADED = "DocumentUploaded"
ALLOWED_TYPES = frozenset({"image/jpeg", "image/png", "image/heic", "application/pdf"})
SNIFF_BYTES = 16
MAX_PENDING_UPLOADS = 20  # U-09: no number in the docs, so a default; tune with product
PENDING_WINDOW_SECONDS = (
    2 * PRESIGN_TTL_SECONDS
)  # older pending rows are abandoned and do not count
_HEIC_BRANDS = {b"heic", b"heix", b"heim", b"heis", b"mif1", b"msf1"}


def quarantine_key(profile_id: UUID, document_id: UUID) -> str:
    """Server-generated key: no user-controlled filename (U-11)."""
    return f"quarantine/{profile_id}/{document_id}"


def sniff_mime(head: bytes) -> str | None:
    """Detect the real type from leading bytes; None when not an allowed format."""
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head[4:8] == b"ftyp" and head[8:12] in _HEIC_BRANDS:
        return "image/heic"
    return None


@dataclass(frozen=True)
class Document:
    id: UUID
    profile_id: UUID
    storage_key: str
    mime: str
    status: str
    sha256: str = ""


@dataclass(frozen=True)
class Presigned:
    url: str
    headers: dict[str, str]
    expires_in: int


class DocumentNotFound(NotFound):
    """Also used for other users' profiles/documents: existence is never leaked."""

    def __init__(self) -> None:
        super().__init__("Resource not found.")


CONSENT_PROCESSING = "health_data_processing"  # withdrawing it stops new uploads (T106)


class ConsentWithdrawn(Forbidden):
    slug = "consent-withdrawn"
    title = "Consent withdrawn"


class FileTooLarge(AppError):
    status = 413
    code = "MEDILENS-413"
    slug = "file-too-large"
    title = "File too large"


class UnsupportedFileType(AppError):
    status = 415
    code = "MEDILENS-415"
    slug = "unsupported-file-type"
    title = "Unsupported file type"


class DuplicateDocument(AppError):
    status = 409
    code = "MEDILENS-409"
    slug = "duplicate-document"
    title = "Duplicate document"


class UploadMissing(AppError):
    status = 409
    code = "MEDILENS-409"
    slug = "upload-missing"
    title = "Upload not found in storage"


class TooManyPendingUploads(AppError):
    status = 429
    code = "MEDILENS-429"
    slug = "too-many-pending-uploads"
    title = "Too many pending uploads"
