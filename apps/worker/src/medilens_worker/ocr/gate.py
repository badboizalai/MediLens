"""Pure quality-gate decision (BR-011). Thresholds follow blur_check.py (ai-ml-engineer skill)."""

from dataclasses import dataclass

from medilens_worker.ocr.types import Metrics, RetakeReason


@dataclass(frozen=True)
class GateConfig:
    blur_threshold: float = 100.0
    min_brightness: float = 60.0
    min_ink_ratio: float = 0.005
    max_ink_ratio: float = 0.5


DEFAULT_GATE = GateConfig()


def decide(m: Metrics, cfg: GateConfig = DEFAULT_GATE) -> RetakeReason | None:
    """First failing check wins. Order: wrong subject, then lighting, then focus."""
    if not cfg.min_ink_ratio <= m.ink_ratio <= cfg.max_ink_ratio:
        return RetakeReason.NOT_A_DOCUMENT
    if m.brightness < cfg.min_brightness:
        return RetakeReason.TOO_DARK
    if m.blur < cfg.blur_threshold:
        return RetakeReason.BLURRY
    return None


def quality_score(m: Metrics, cfg: GateConfig = DEFAULT_GATE) -> float:
    """0..1 blend of sharpness (70%) and exposure (30%). For ranking/UI, not a gate."""
    sharp = min(m.blur / (2 * cfg.blur_threshold), 1.0)
    expo = 1.0 - min(abs(m.brightness - 140.0) / 140.0, 1.0)
    return round(0.7 * sharp + 0.3 * expo, 3)
