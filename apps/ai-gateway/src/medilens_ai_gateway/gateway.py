"""Gateway core: allowlist -> redact (fail closed) -> cache -> provider (timeout) -> meter -> log."""

import hashlib
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, replace

from .config import GatewayConfig
from .providers import Provider, ProviderResult
from .redaction import redact as default_redact

log = logging.getLogger("medilens.ai_gateway")


class GatewayError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


@dataclass(frozen=True)
class CompletionRequest:
    tenant_id: str
    profile_id: str
    prompt: str
    model: str | None = None
    max_output_tokens: int = 400


@dataclass(frozen=True)
class CompletionResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    cached: bool


class Gateway:
    def __init__(
        self,
        config: GatewayConfig,
        provider: Provider,
        redactor: Callable[[str], str] = default_redact,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.provider = provider
        self.redactor = redactor
        self.clock = clock
        self._cache: dict[str, tuple[float, CompletionResponse]] = {}
        self.total_cost_usd = 0.0
        self.total_tokens = 0
        self._pool = ThreadPoolExecutor(max_workers=4)

    def cache_key(self, req: CompletionRequest, model: str, redacted: str) -> str:
        """Scoped by tenant + profile + prompt version + model (O-02, A-09); only a hash is kept."""
        parts = [req.tenant_id, req.profile_id, self.config.prompt_version, model, redacted]
        return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()

    def _redact(self, text: str, what: str) -> str:
        try:
            out = self.redactor(text)
            if not isinstance(out, str):
                raise TypeError("redactor returned non-str")
            return out
        except Exception as exc:  # fail closed (O-03): nothing is sent or logged
            log.error("redaction_failed stage=%s", what)
            raise GatewayError("redaction_failed", f"{what} blocked: redaction error") from exc

    def complete(self, req: CompletionRequest) -> CompletionResponse:
        if not req.tenant_id or not req.profile_id:
            raise GatewayError("scope_required", "tenant_id and profile_id are required")
        model = req.model or self.config.default_model
        if model not in self.config.allowlist:
            raise GatewayError("model_not_allowed", "model is not in the allowlist")
        redacted = self._redact(req.prompt, "request")

        key = self.cache_key(req, model, redacted)
        now = self.clock()
        hit = self._cache.get(key)
        if hit and now - hit[0] < self.config.cache_ttl_s:
            return replace(hit[1], cached=True, cost_usd=0.0)

        future = self._pool.submit(
            self.provider.complete,
            model=model,
            prompt=redacted,
            max_output_tokens=req.max_output_tokens,
        )
        try:
            result: ProviderResult = future.result(timeout=self.config.timeout_s)
        except FutureTimeout as exc:
            future.cancel()
            raise GatewayError("provider_timeout", "provider call timed out") from exc
        except Exception as exc:
            raise GatewayError("provider_error", "provider call failed") from exc

        out = self._redact(result.text, "response")
        cost = self._cost(model, result)
        self.total_cost_usd += cost
        self.total_tokens += result.input_tokens + result.output_tokens
        resp = CompletionResponse(
            out, model, result.input_tokens, result.output_tokens, cost, cached=False
        )
        self._cache[key] = (now, resp)
        log.info(
            "completion model=%s in=%d out=%d cost=%.6f prompt=%s response=%s",
            model,
            result.input_tokens,
            result.output_tokens,
            cost,
            redacted,
            out,
        )
        return resp

    def _cost(self, model: str, r: ProviderResult) -> float:
        p = self.config.prices.get(model)
        if p is None:
            return 0.0
        return (r.input_tokens * p.input + r.output_tokens * p.output) / 1_000_000
