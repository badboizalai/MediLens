from typing import Protocol


class OcrProvider(Protocol):
    def read(self, image: bytes, lang: str = "vi") -> str: ...


class LlmProvider(Protocol):
    """Called only through the AI Gateway, after PII redaction."""

    def extract(self, prompt: str, schema: dict) -> dict: ...
