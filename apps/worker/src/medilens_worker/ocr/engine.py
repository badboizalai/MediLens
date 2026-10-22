"""OCR engine port and a deterministic fake for tests."""

from typing import Protocol

from medilens_worker.ocr.types import OcrBox


class OcrEngine(Protocol):
    name: str

    def recognize(self, image: bytes) -> list[OcrBox]:
        """`image` is an encoded (PNG/JPEG) page. Boxes in reading order."""
        ...


class FakeOcrEngine:
    """Returns canned lines; counts calls."""

    name = "fake"

    def __init__(self, lines: list[str] | None = None) -> None:
        self.lines = lines if lines is not None else ["Benh vien Thu Nghiem", "Rang 36: sau"]
        self.calls = 0

    def recognize(self, image: bytes) -> list[OcrBox]:
        self.calls += 1
        return [
            OcrBox(t, 10, 10 + 30 * i, 400, 36 + 30 * i, 0.99) for i, t in enumerate(self.lines)
        ]
