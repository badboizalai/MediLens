"""Provider interface plus a deterministic stub. Real adapters (Anthropic/Bedrock) come later."""

import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderResult:
    text: str
    input_tokens: int
    output_tokens: int
    confidence: float | None = None  # None = not reported => no escalation
    schema_valid: bool = True


class Provider(Protocol):
    def complete(self, *, model: str, prompt: str, max_output_tokens: int) -> ProviderResult: ...


class StubProvider:
    """Deterministic, offline. Records what it received so tests can assert nothing raw leaks."""

    def __init__(self, delay_s: float = 0.0) -> None:
        self.delay_s = delay_s
        self.calls: list[dict[str, object]] = []

    def complete(self, *, model: str, prompt: str, max_output_tokens: int) -> ProviderResult:
        self.calls.append({"model": model, "prompt": prompt})
        if self.delay_s:
            time.sleep(self.delay_s)
        text = f"stub:{model}:{len(prompt)}"
        return ProviderResult(
            text=text,
            input_tokens=max(1, len(prompt.split())),
            output_tokens=min(max_output_tokens, max(1, len(text.split()))),
        )
