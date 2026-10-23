"""Gateway core: allowlist -> redact (fail closed) -> cache -> provider (timeout) -> meter -> log."""

import hashlib
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, field, replace

from .cache import SemanticCache
from .config import GatewayConfig
from .guardrails import check_input, check_output
from .providers import Provider, ProviderResult
from .quota import QuotaExceeded, TokenQuota
from .redaction import redact as default_redact

log = logging.getLogger("medilens.ai_gateway")


class GatewayError(Exception):
    def __init__(self, code: str, message: str = "", retry_after_s: int | None = None) -> None:
        super().__init__(message or code)
        self.code = code
        self.retry_after_s = retry_after_s


@dataclass(frozen=True)
class CompletionRequest:
    tenant_id: str
    profile_id: str
    prompt: str
    model: str | None = None
    max_output_tokens: int = 400
    tier: str | None = None  # None = single call (v0); "auto" = cascade S -> M
    document_id: str | None = None  # opaque id, metering only
    traffic: str | None = None  # "qa" = explanation/Q&A: safety guardrails apply (BR-023/041/042)
    locale: str = "vi"  # language of guardrail copy


@dataclass(frozen=True)
class CompletionResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    cached: bool
    confidence: float | None = None
    tier: str | None = None
    escalated: bool = False
    needs_review: bool = False
    guardrail: dict[str, str] | None = None  # {category, action} when a guardrail fired


@dataclass
class DocumentUsage:
    cost_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    tier_counts: dict[str, int] = field(default_factory=dict)


class Gateway:
    def __init__(
        self,
        config: GatewayConfig,
        provider: Provider,
        redactor: Callable[[str], str] = default_redact,
        clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], float] = time.time,
    ) -> None:
        self.config = config
        self.provider = provider
        self.redactor = redactor
        self.clock = clock
        self._cache: dict[str, tuple[float, CompletionResponse]] = {}
        self.qa_cache: SemanticCache[CompletionResponse] = SemanticCache(
            clock, ttl_s=config.cache_ttl_s
        )
        self.quota = TokenQuota(config.daily_token_quota, wall_clock)
        self.total_cost_usd = 0.0
        self.total_tokens = 0
        self._docs: dict[str, DocumentUsage] = {}
        self._pool = ThreadPoolExecutor(max_workers=4)

    def cache_key(self, req: CompletionRequest, model: str, redacted: str) -> str:
        """Scoped by tenant + profile + prompt version + model (O-02, A-09); only a hash is kept."""
        parts = [
            req.tenant_id,
            req.profile_id,
            req.locale,
            self.config.prompt_version,
            model,
            redacted,
        ]
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

    def document_usage(self, document_id: str) -> DocumentUsage | None:
        return self._docs.get(document_id)

    def _guarded(self, category: str, action: str, text: str) -> CompletionResponse:
        log.info("guardrail category=%s action=%s", category, action)  # never the prompt
        return CompletionResponse(
            text, "guardrail", 0, 0, 0.0, cached=False,
            guardrail={"category": category, "action": action},
        )  # fmt: skip

    def complete(self, req: CompletionRequest) -> CompletionResponse:
        if not req.tenant_id or not req.profile_id:
            raise GatewayError("scope_required", "tenant_id and profile_id are required")
        qa = req.traffic == "qa"
        if qa and (hit := check_input(req.prompt, req.locale)):  # no redaction/provider call
            return self._guarded(hit.category, hit.action, hit.text)
        scope = (req.tenant_id, req.profile_id, req.locale, self.config.prompt_version)
        question = ""
        if qa:  # key on the REDACTED question; a hit consumes no quota
            question = self._redact(req.prompt, "request")
            if (cached := self.qa_cache.get(scope, question)) is not None:
                return replace(cached, cached=True, cost_usd=0.0)
        user = (req.tenant_id, req.profile_id)
        try:
            self.quota.check(user)
        except QuotaExceeded as e:
            raise GatewayError("quota_exceeded", str(e), e.retry_after_s) from e
        resp = self._route(req)
        if not resp.cached:  # exact-cache hits are free too
            self.quota.charge(user, resp.input_tokens + resp.output_tokens)
        if not qa:
            return resp
        if hit := check_output(resp.text, req.locale):  # refusals are never cached
            return replace(self._guarded(hit.category, hit.action, hit.text), model=resp.model,
                           input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
                           cost_usd=resp.cost_usd, tier=resp.tier)  # fmt: skip
        self.qa_cache.put(scope, question, resp)
        return resp

    def _route(self, req: CompletionRequest) -> CompletionResponse:
        if req.tier is None:
            model = req.model or self.config.default_model
            self._check_allowed(model)
            return self._call(req, model, "direct")
        if req.tier != "auto":
            raise GatewayError("tier_invalid", "tier must be 'auto' or absent")
        s_model, m_model = self.config.tier_s_model, self.config.tier_m_model
        self._check_allowed(s_model)
        self._check_allowed(m_model)
        first = self._call(req, s_model, "S")
        if not self._low(first):
            return first
        # Exactly one escalation; never beyond M. Each call is redacted afresh (fail closed).
        second = self._call(req, m_model, "M")
        return replace(
            second,
            escalated=True,
            needs_review=self._low(second),
            input_tokens=first.input_tokens + second.input_tokens,
            output_tokens=first.output_tokens + second.output_tokens,
            cost_usd=first.cost_usd + second.cost_usd,
        )

    def _check_allowed(self, model: str) -> None:
        if model not in self.config.allowlist:
            raise GatewayError("model_not_allowed", "model is not in the allowlist")

    def _low(self, r: CompletionResponse) -> bool:
        return (r.confidence is not None and r.confidence < self.config.escalation_threshold) or (
            r.needs_review
        )

    def _call(self, req: CompletionRequest, model: str, tier: str) -> CompletionResponse:
        redacted = self._redact(req.prompt, "request")

        key = self.cache_key(req, model, redacted)
        now = self.clock()
        hit = self._cache.get(key)
        if hit and now - hit[0] < self.config.cache_ttl_s:
            return replace(hit[1], cached=True, cost_usd=0.0, tier=tier)

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
            out,
            model,
            result.input_tokens,
            result.output_tokens,
            cost,
            cached=False,
            confidence=result.confidence,
            tier=tier,
            needs_review=not result.schema_valid,  # escalation trigger; final value set by complete()
        )
        if req.document_id:
            u = self._docs.setdefault(req.document_id, DocumentUsage())
            u.cost_usd += cost
            u.tokens_in += result.input_tokens
            u.tokens_out += result.output_tokens
            u.tier_counts[tier] = u.tier_counts.get(tier, 0) + 1
        self._cache[key] = (now, resp)
        log.info(
            "completion model=%s tier=%s doc=%s in=%d out=%d cost=%.6f prompt=%s response=%s",
            model,
            tier,
            req.document_id,
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
        return (r.input_tokens * p.input + r.output_tokens * p.output) / 1_000
