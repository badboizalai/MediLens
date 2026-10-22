"""Pillow-only rendering (no browser needed) and photo-like degradations."""

from __future__ import annotations

import io
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1000, 1300
FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/Library/Fonts",
    "C:/Windows/Fonts",
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    try:  # Pillow bundles no Vietnamese-capable font; fall back to system lookup
        return ImageFont.truetype(name, size)
    except OSError as e:
        raise RuntimeError("DejaVu Sans font (Vietnamese diacritics) not found") from e


def render_clean(header: list[str], lines: list[str]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (250, 249, 245))
    d = ImageDraw.Draw(img)
    y = 50
    d.text((50, y), header[0], font=_font(22, True), fill=(20, 20, 20))
    y += 70
    for h in header[1:]:
        d.text((50, y), h, font=_font(24), fill=(20, 20, 20))
        y += 40
    d.line([(50, y + 5), (WIDTH - 50, y + 5)], fill=(60, 60, 60), width=2)
    y += 30
    body = _font(25)
    for ln in lines:
        d.text((50, y), ln, font=body, fill=(15, 15, 15))
        y += 42
    d.rectangle([(50, HEIGHT - 120), (400, HEIGHT - 50)], outline=(120, 120, 200), width=2)
    d.text((62, HEIGHT - 100), "SYNTHETIC - TEST ONLY", font=_font(22, True), fill=(120, 120, 200))
    return img


def _gradient_multiply(img: Image.Image, strength: float, rng: random.Random) -> Image.Image:
    """Diagonal shadow: darkens one side by up to `strength`."""
    w, h = img.size
    grad = Image.linear_gradient("L").resize((w, h))
    if rng.random() < 0.5:
        grad = grad.transpose(Image.FLIP_TOP_BOTTOM)
    # grad 0..255 -> factor 1-strength..1
    factor = grad.point(lambda v: int(255 * (1 - strength * (1 - v / 255))))
    shade = Image.merge("RGB", (factor, factor, factor))
    out = Image.new("RGB", (w, h))
    px_a, px_b, px_o = img.load(), shade.load(), out.load()
    for yy in range(h):
        for xx in range(w):
            a, b = px_a[xx, yy], px_b[xx, yy]
            px_o[xx, yy] = (a[0] * b[0] // 255, a[1] * b[1] // 255, a[2] * b[2] // 255)
    return out


def _fold(img: Image.Image, rng: random.Random) -> tuple[Image.Image, int]:
    y = rng.randint(HEIGHT // 3, 2 * HEIGHT // 3)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(0, y), (WIDTH, y)], fill=(90, 90, 90, 150), width=3)
    d.rectangle([(0, y + 3), (WIDTH, y + 18)], fill=(0, 0, 0, 28))
    return img, y


def degrade(img: Image.Image, quality: str, rng: random.Random) -> tuple[Image.Image, list[dict]]:
    """medium: blur + skew. poor: stronger blur + skew + shadow + fold."""
    ops: list[dict] = []
    poor = quality == "poor"
    sigma = round(rng.uniform(1.2, 2.0) if poor else rng.uniform(0.6, 1.2), 2)
    img = img.filter(ImageFilter.GaussianBlur(sigma))
    ops.append({"type": "blur", "sigma": sigma})
    angle = round(rng.uniform(-7, 7), 2)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(210, 205, 195))
    ops.append({"type": "skew", "angle_deg": angle})
    if poor:
        strength = round(rng.uniform(0.35, 0.6), 2)
        img = _gradient_multiply(img, strength, rng)
        ops.append({"type": "shadow", "strength": strength})
        img, y = _fold(img, rng)
        ops.append({"type": "fold", "y": y})
    return img, ops


def to_jpeg(img: Image.Image, path: Path, quality: int = 80) -> None:
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=False)
    path.write_bytes(buf.getvalue())
