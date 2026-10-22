"""Production engine: PaddleOCR text detection + VietOCR recognition.

Chosen by ml/eval/ocr_bakeoff/REPORT.md (lowest CER, 4.40% vs 15.63% on golden-v0).
Heavy deps (`ocr` extra) are imported lazily in load() so base installs stay light.
"""

from medilens_worker.ocr.types import OcrBox


class EngineUnavailable(RuntimeError):
    pass


class PaddleVietOcrEngine:
    name = "paddle-vietocr"

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
            raise EngineUnavailable(type(e).__name__) from e

    def recognize(self, image: bytes) -> list[OcrBox]:
        import io  # noqa: PLC0415

        import numpy as np  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415

        if self._det is None:
            self.load()
        img = Image.open(io.BytesIO(image)).convert("RGB")
        polys = self._det.ocr(np.asarray(img)[:, :, ::-1], rec=False, cls=False)[0] or []
        boxes = []
        for poly in polys:
            xs, ys = [p[0] for p in poly], [p[1] for p in poly]
            x0, y0 = max(0, int(min(xs)) - 2), max(0, int(min(ys)) - 2)
            x1, y1 = int(max(xs)) + 2, int(max(ys)) + 2
            boxes.append(OcrBox(self._rec.predict(img.crop((x0, y0, x1, y1))), x0, y0, x1, y1))
        return sorted(boxes, key=lambda b: (b.y0, b.x0))
