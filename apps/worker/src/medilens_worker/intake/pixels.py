"""Pre-decode pixel cap (decompression-bomb guard): read dimensions from the header only."""

import struct

# A4 at 600 dpi is ~35 MP; 50 MP leaves headroom for phone cameras yet bounds a decoded
# BGR array to ~150 MB. Raw upload is already capped at 20 MB (BR-010).
MAX_IMAGE_PIXELS = 50_000_000
_SOF = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}


def _dims(data: bytes) -> tuple[int, int] | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and data[12:16] == b"IHDR" and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 <= len(data) and data[i] == 0xFF:
            m = data[i + 1]
            if m in _SOF:
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
    return None


def declared_pixels(data: bytes) -> int | None:
    """Width x height from the PNG/JPEG header, or None if unreadable."""
    d = _dims(data)
    return d[0] * d[1] if d else None


def within_pixel_cap(data: bytes) -> bool:
    """True only if the header declares dimensions and w*h <= MAX_IMAGE_PIXELS (fails closed)."""
    n = declared_pixels(data)
    return n is not None and 0 < n <= MAX_IMAGE_PIXELS
