"""Apply the worker's S6-T55 crop + perspective + deskew to golden pages before OCR.

Calls crop_document/deskew directly (not preprocess_page) so the quality gate never drops a
page: CER is then comparable page-for-page with the unprocessed run.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

WORKER_SRC = Path(__file__).resolve().parents[4] / "apps" / "worker" / "src"


def preprocess_pages(pages: list, out_dir: Path) -> list:
    sys.path.insert(0, str(WORKER_SRC))
    import cv2  # noqa: PLC0415
    from medilens_worker.ocr.preprocess import crop_document, deskew  # noqa: PLC0415

    out_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for p in pages:
        img = cv2.imread(str(p.image))
        dst = out_dir / f"{p.doc_id}_{p.variant}.png"
        cv2.imwrite(str(dst), deskew(crop_document(img)))
        out.append(dataclasses.replace(p, image=dst))
    return out
