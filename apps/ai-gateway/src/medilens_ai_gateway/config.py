"""Gateway config loaded from TOML (model ids and prices live here, not in code)."""

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "gateway.toml"


@dataclass(frozen=True)
class Price:
    input: float  # USD per 1M tokens (assumption)
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


def load_config(path: Path | str = DEFAULT_PATH) -> GatewayConfig:
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    cfg = GatewayConfig(
        default_model=raw["default_model"],
        allowlist=frozenset(raw["allowlist"]["models"]),
        prices={k: Price(**v) for k, v in raw.get("prices_usd_per_mtok", {}).items()},
        timeout_s=float(raw.get("timeout_s", 20.0)),
        prompt_version=raw.get("prompt_version", "v0"),
        cache_ttl_s=int(raw.get("cache_ttl_s", 3600)),
        provider=raw.get("providers", {}).get("default", "stub"),
    )
    if cfg.default_model not in cfg.allowlist:
        raise ValueError("default_model must be in allowlist")
    return cfg
