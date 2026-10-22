"""Plain data types for the preprocess/OCR steps. No heavy imports."""

from dataclasses import dataclass, field
from enum import Enum


class RetakeReason(str, Enum):  # StrEnum needs 3.11
    """User-facing reason codes: the client maps these to localized retake tips."""

    BLURRY = "blurry"
    TOO_DARK = "too_dark"
    NOT_A_DOCUMENT = "not_a_document"


class RetakeRequired(Exception):
    """A page failed the quality gate. Carries only the code (no PHI)."""

    def __init__(self, page: int, reason: RetakeReason) -> None:
        super().__init__(f"retake:{reason.value}")
        self.page, self.reason = page, reason


@dataclass(frozen=True)
class Metrics:
    blur: float  # variance of Laplacian at short side 1000 px
    brightness: float  # mean gray, 0..255
    ink_ratio: float  # fraction of dark text-like pixels


@dataclass(frozen=True)
class PreprocessedPage:
    page: int
    image: bytes  # PNG, cropped and deskewed
    quality: float  # 0..1
    metrics: Metrics


@dataclass(frozen=True)
class OcrBox:
    text: str
    x0: int
    y0: int
    x1: int
    y1: int
    confidence: float | None = None


@dataclass(frozen=True)
class OcrPage:
    page: int
    text: str
    boxes: list[OcrBox] = field(default_factory=list)
    quality: float = 0.0
