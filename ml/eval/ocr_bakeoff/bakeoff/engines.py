"""OCR engine adapters behind one Protocol. Heavy imports are lazy (inside load())."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class EngineUnavailable(RuntimeError):
    """Engine cannot run here (missing dep, weights, API key). Reported as 'not run'."""


@dataclass
class OcrResult:
    text: str
    usd: float | None = None  # engine-reported cost (API engines); None = harness estimates compute


class OcrEngine(Protocol):
    name: str

    def load(self) -> None:
        """Heavy init (weights, clients). Raise EngineUnavailable if it cannot run."""

    def recognize(self, image: Path) -> OcrResult: ...


class PaddleEngine:
    """PaddleOCR PP-OCRv3 detection + latin (Vietnamese) recognition, CPU."""

    name = "paddle"

    def __init__(self) -> None:
        self._ocr = None

    def load(self) -> None:
        try:
            from paddleocr import PaddleOCR  # noqa: PLC0415

            self._ocr = PaddleOCR(lang="vi", use_angle_cls=False, show_log=False)
        except Exception as e:  # noqa: BLE001 - any install/download failure means "not run"
            raise EngineUnavailable(f"{type(e).__name__}: {e}") from e

    def recognize(self, image: Path) -> OcrResult:
        res = self._ocr.ocr(str(image), cls=False)[0] or []
        return OcrResult("\n".join(text for _, (text, _) in res))


class VietOcrEngine:
    """PaddleOCR text detection + VietOCR (vgg_transformer) recognition per line crop, CPU."""

    name = "vietocr"

    def __init__(self) -> None:
        self._det = None
        self._rec = None

    def load(self) -> None:
        try:
            from paddleocr import PaddleOCR  # noqa: PLC0415
            from vietocr.tool.config import Cfg  # noqa: PLC0415
            from vietocr.tool.predictor import Predictor  # noqa: PLC0415

            self._det = PaddleOCR(lang="vi", use_angle_cls=False, show_log=False)
            cfg = Cfg.load_config_from_name("vgg_transformer")
            cfg["device"] = "cpu"
            cfg["predictor"]["beamsearch"] = False
            cfg["cnn"]["pretrained"] = False
            self._rec = Predictor(cfg)
        except Exception as e:  # noqa: BLE001
            raise EngineUnavailable(f"{type(e).__name__}: {e}") from e

    def recognize(self, image: Path) -> OcrResult:
        from PIL import Image  # noqa: PLC0415

        img = Image.open(image).convert("RGB")
        boxes = self._det.ocr(str(image), rec=False, cls=False)[0] or []
        lines = []
        for box in boxes:
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            x0, y0, x1, y1 = (
                max(0, int(min(xs)) - 2),
                max(0, int(min(ys)) - 2),
                int(max(xs)) + 2,
                int(max(ys)) + 2,
            )
            lines.append((y0, x0, self._rec.predict(img.crop((x0, y0, x1, y1)))))
        return OcrResult("\n".join(t for _, _, t in sorted(lines)))


class LlmVisionEngine:
    """Anthropic vision transcription. Needs ANTHROPIC_API_KEY; synthetic images only.

    Prices are illustrative (plan 28.4 Tier M: 1 / 5 USD per million tokens); override via env.
    """

    name = "llm-vision"
    PROMPT = "Transcribe all text in this image exactly, line by line. Output only the text."

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("BAKEOFF_LLM_MODEL", "claude-haiku-4-5")
        self.usd_in = float(os.environ.get("BAKEOFF_LLM_USD_IN_PER_M", "1.0")) / 1e6
        self.usd_out = float(os.environ.get("BAKEOFF_LLM_USD_OUT_PER_M", "5.0")) / 1e6
        self._client = None

    def load(self) -> None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise EngineUnavailable("ANTHROPIC_API_KEY not set")
        try:
            import anthropic  # noqa: PLC0415

            self._client = anthropic.Anthropic()
        except Exception as e:  # noqa: BLE001
            raise EngineUnavailable(f"{type(e).__name__}: {e}") from e

    def recognize(self, image: Path) -> OcrResult:
        data = base64.standard_b64encode(image.read_bytes()).decode()
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": data},
                        },
                        {"type": "text", "text": self.PROMPT},
                    ],
                }
            ],
        )
        usd = msg.usage.input_tokens * self.usd_in + msg.usage.output_tokens * self.usd_out
        return OcrResult("".join(b.text for b in msg.content if b.type == "text"), usd)


ENGINES: dict[str, type] = {
    "paddle": PaddleEngine,
    "vietocr": VietOcrEngine,
    "llm-vision": LlmVisionEngine,
}
