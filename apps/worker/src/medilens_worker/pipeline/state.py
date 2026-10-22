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


ALLOWED: dict[DocStatus, frozenset[DocStatus]] = {
    DocStatus.UPLOADED: frozenset({DocStatus.VALIDATED, DocStatus.FAILED}),
    DocStatus.VALIDATED: frozenset({DocStatus.PREPROCESSED, DocStatus.FAILED}),
    DocStatus.PREPROCESSED: frozenset({DocStatus.CLASSIFIED, DocStatus.FAILED}),
    DocStatus.CLASSIFIED: frozenset({DocStatus.OCR_DONE, DocStatus.FAILED}),
    DocStatus.OCR_DONE: frozenset({DocStatus.EXTRACTED, DocStatus.FAILED}),
    DocStatus.EXTRACTED: frozenset({DocStatus.NEEDS_REVIEW, DocStatus.FAILED}),
    DocStatus.NEEDS_REVIEW: frozenset({DocStatus.CONFIRMED}),  # user action (API)
    DocStatus.CONFIRMED: frozenset(),
    DocStatus.FAILED: frozenset(),
}


class InvalidTransition(Exception):
    def __init__(self, current: DocStatus, to: DocStatus) -> None:
        super().__init__(f"illegal transition {current.value} -> {to.value}")
        self.current, self.to = current, to


def guard_transition(current: DocStatus, to: DocStatus) -> DocStatus:
    """Return `to` if the edge is allowed, else raise InvalidTransition."""
    if to not in ALLOWED[current]:
        raise InvalidTransition(current, to)
    return to


class StatusRepo:
    """In-memory document status store (DB-backed impl comes with S5-T43+)."""

    def __init__(self) -> None:
        self._s: dict[str, DocStatus] = {}

    def get(self, document_id: str) -> DocStatus:
        return self._s.get(document_id, DocStatus.UPLOADED)

    def set(self, document_id: str, status: DocStatus) -> None:
        self._s[document_id] = guard_transition(self.get(document_id), status)
