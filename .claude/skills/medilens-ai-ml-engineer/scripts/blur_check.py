#!/usr/bin/env python3
"""Image quality gate for uploaded record photos (BR-011).

Usage:
    python blur_check.py <image> [<image> ...] [--threshold 100] [--min-short-side 1000]

Prints JSON per image: {"file", "ok", "blur_score", "short_side", "brightness", "reasons"}.
Blur score = variance of the Laplacian on a grayscale image resized so the
short side is 1000 px (so scores are comparable across resolutions).
Requires: pip install opencv-python numpy
"""

import argparse
import json

import cv2  # type: ignore
import numpy as np  # type: ignore


def assess(path: str, threshold: float, min_short: int) -> dict:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return {"file": path, "ok": False, "reasons": ["unreadable"]}
    h, w = img.shape[:2]
    short = min(h, w)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    scale = 1000.0 / short
    norm = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    blur = float(cv2.Laplacian(norm, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    reasons = []
    if short < min_short:
        reasons.append("low_resolution")
    if blur < threshold:
        reasons.append("blurry")
    if brightness < 60:
        reasons.append("too_dark")
    if brightness > 235:
        reasons.append("overexposed")
    return {
        "file": path,
        "ok": not reasons,
        "blur_score": round(blur, 1),
        "short_side": short,
        "brightness": round(brightness, 1),
        "reasons": reasons,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--threshold", type=float, default=100.0)
    ap.add_argument("--min-short-side", type=int, default=1000)
    a = ap.parse_args()
    for p in a.images:
        print(json.dumps(assess(p, a.threshold, a.min_short_side), ensure_ascii=False))


if __name__ == "__main__":
    main()
