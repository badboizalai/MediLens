"""Document processing state machine (see plan §8.1 / §9.1)."""

from enum import Enum


class DocStatus(str, Enum):  # StrEnum needs 3.11
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    PREPROCESSED = "preprocessed"
    CLASSIFIED = "classified"
    OCR_DONE = "ocr_done"
    EXTRACTED = "extracted"
    NEEDS_REVIEW = "needs_review"
    CONFIRMED = "confirmed"
    FAILED = "failed"


ORDER = [
    DocStatus.UPLOADED,
    DocStatus.VALIDATED,
    DocStatus.PREPROCESSED,
    DocStatus.CLASSIFIED,
    DocStatus.OCR_DONE,
    DocStatus.EXTRACTED,
    DocStatus.NEEDS_REVIEW,
    DocStatus.CONFIRMED,
]


def next_status(current: DocStatus) -> DocStatus | None:
    i = ORDER.index(current)
    return ORDER[i + 1] if i + 1 < len(ORDER) else None
