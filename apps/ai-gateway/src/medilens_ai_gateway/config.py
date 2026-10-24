"""Gateway config loaded from TOML (model ids and prices live here, not in code)."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "gateway.toml"


DEFAULT_ESCALATION_THRESHOLD = 0.7  # BR-012: fields below 0.7 need user confirmation
DEFAULT_DAILY_TOKEN_QUOTA = (
    50_000  # SEC-AI-07: input+output tokens per user per UTC day (assumption)
)


@dataclass(frozen=True)
class Price:
    input: float  # USD per 1K tokens (assumption)
    output: float


@dataclass(frozen=True)
class GatewayConfig:
    default_model: str
    allowlist: frozenset[str]
    prices: dict[str, Price]
    timeout_s: float = 20.0
    prompt_version: str = "v0"
    cache_ttl_s: int = 3600
    provider: str = "stub"
    tier_s_model: str = ""
    tier_m_model: str = ""
    escalation_threshold: float = DEFAULT_ESCALATION_THRESHOLD
    daily_token_quota: int = DEFAULT_DAILY_TOKEN_QUOTA


def load_config(path: Path | str = DEFAULT_PATH) -> GatewayConfig:
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    cfg = GatewayConfig(
        default_model=raw["default_model"],
        allowlist=frozenset(raw["allowlist"]["models"]),
        prices={k: Price(**v) for k, v in raw.get("prices_usd_per_1k", {}).items()},
        timeout_s=float(raw.get("timeout_s", 20.0)),
        prompt_version=raw.get("prompt_version", "v0"),
        cache_ttl_s=int(raw.get("cache_ttl_s", 3600)),
        provider=raw.get("providers", {}).get("default", "stub"),
        tier_s_model=os.environ.get("AI_GATEWAY_TIER_S_MODEL")
        or raw.get("tier_s_model", raw["default_model"]),
        tier_m_model=os.environ.get("AI_GATEWAY_TIER_M_MODEL")
        or raw.get("tier_m_model", raw["default_model"]),
        escalation_threshold=float(
            os.environ.get("AI_GATEWAY_ESCALATION_THRESHOLD")
            or raw.get("escalation_threshold", DEFAULT_ESCALATION_THRESHOLD)
        ),
        daily_token_quota=int(
            os.environ.get("AI_GATEWAY_DAILY_TOKEN_QUOTA")
            or raw.get("daily_token_quota", DEFAULT_DAILY_TOKEN_QUOTA)
        ),
    )
    if cfg.default_model not in cfg.allowlist:
        raise ValueError("default_model must be in allowlist")
    return cfg
