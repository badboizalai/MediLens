"""OpenCV preprocessing: metrics, document crop + perspective, deskew.

Requires the `ocr` extra (opencv-python-headless, numpy); imported lazily by the service.
"""

import cv2
import numpy as np

from medilens_worker.intake.pixels import within_pixel_cap
from medilens_worker.ocr.gate import DEFAULT_GATE, GateConfig, decide, quality_score
from medilens_worker.ocr.types import Metrics, PreprocessedPage, RetakeReason

MIN_DOC_AREA = 0.2  # a page quad must cover at least this share of the frame
MAX_DOC_AREA = 0.95  # a quad this large is the frame itself, not a page on a desk
MAX_DESKEW_DEG = 15.0
MIN_SIDE_FRAC = 0.3  # warped page sides must span this share of the frame
QUAD_EPS = 0.02  # approxPolyDP epsilon as a share of the contour perimeter
MIN_EDGE_STEP = 12  # min grey step across the border; less is an inner box, not a desk
RING_PX = 12  # width of the strips compared on each side of the border
GAP_PX = 8  # skipped next to the border so a drawn line does not count
FLUSH_PX = 3  # a quad edge this close to the frame border lies on the border
MAX_FLUSH_SIDES = (
    2  # a page on a desk is flush with at most two sides; three is a slice of the frame
)
CANNY_LO, CANNY_HI = 30, 90  # edge thresholds for pages with little contrast to the desk


def decode(data: bytes) -> np.ndarray | None:
    if not within_pixel_cap(data):  # oversized or unreadable header: skip decode, gate says retake
        return None
    return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)


def _ink(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 15
    )


def _ink_small(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 6
    )


def measure(img: np.ndarray) -> Metrics:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    s = 1000.0 / min(h, w)
    norm = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    blur = float(cv2.Laplacian(norm, cv2.CV_64F).var())
    # Ink is measured on a small copy so a blurred page still shows its text mass.
    small = cv2.resize(gray, (int(w * 250 / min(h, w)), 250), interpolation=cv2.INTER_AREA)
    ink = float(np.count_nonzero(_ink_small(small))) / small.size
    return Metrics(blur=blur, brightness=float(gray.mean()), ink_ratio=ink)


def _order(pts: np.ndarray) -> np.ndarray:
    s, d = pts.sum(axis=1), np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], "float32")


def _masks(gray: np.ndarray):
    """Candidate page masks, cheapest first: Otsu split, then Canny edges for low contrast."""
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    yield cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    edges = cv2.dilate(cv2.Canny(gray, CANNY_LO, CANNY_HI), np.ones((5, 5), np.uint8))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    yield cv2.erode(closed, np.ones((5, 5), np.uint8))  # undo the dilation so the quad is tight


def _has_step(gray: np.ndarray, quad: np.ndarray) -> bool:
    """True if the strip just outside the quad border is darker or brighter than the one inside."""
    fill = np.zeros(gray.shape, np.uint8)
    cv2.fillPoly(fill, [quad.astype(np.int32)], 255)

    def grow(r: int) -> np.ndarray:  # r < 0 erodes
        k = np.ones((2 * abs(r) + 1,) * 2, np.uint8)
        return cv2.dilate(fill, k) if r > 0 else cv2.erode(fill, k)

    # Skip a gap on each side so a drawn border line is not part of either strip.
    inner = (grow(-GAP_PX) > 0) & (grow(-GAP_PX - RING_PX) == 0)
    outer = (grow(GAP_PX + RING_PX) > 0) & (grow(GAP_PX) == 0)
    if not inner.any() or not outer.any():
        return False
    return abs(float(np.median(gray[inner])) - float(np.median(gray[outer]))) >= MIN_EDGE_STEP


def _flush_sides(quad: np.ndarray, h: int, w: int) -> int:
    """Count frame sides (L, R, T, B) that the quad covers along both ends of an edge."""
    x, y = quad[:, 0], quad[:, 1]
    return sum(int((near < FLUSH_PX).sum() >= 2) for near in (x, w - 1 - x, y, h - 1 - y))


def crop_document(img: np.ndarray) -> np.ndarray:
    """Warp the largest page-like quadrilateral to a rectangle; return img if none found."""
    h, w = img.shape[:2]
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    for mask in _masks(gray):
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:3]:
            if cv2.contourArea(c) < MIN_DOC_AREA * h * w:
                break
            if cv2.contourArea(c) > MAX_DOC_AREA * h * w:
                continue
            quad = cv2.approxPolyDP(c, QUAD_EPS * cv2.arcLength(c, True), True)
            if len(quad) != 4:
                continue
            if _flush_sides(quad.reshape(4, 2), h, w) > MAX_FLUSH_SIDES:
                continue  # shadow or table half of the frame, not a page (BUG-13)
            if not _has_step(gray, quad.reshape(4, 2)):
                continue
            src = _order(quad.reshape(4, 2).astype("float32"))
            tw = int(max(np.linalg.norm(src[0] - src[1]), np.linalg.norm(src[3] - src[2])))
            th = int(max(np.linalg.norm(src[0] - src[3]), np.linalg.norm(src[1] - src[2])))
            if tw < MIN_SIDE_FRAC * w or th < MIN_SIDE_FRAC * h:
                continue
            dst = np.array([[0, 0], [tw - 1, 0], [tw - 1, th - 1], [0, th - 1]], "float32")
            m = cv2.getPerspectiveTransform(src, dst)
            return cv2.warpPerspective(img, m, (tw, th), flags=cv2.INTER_CUBIC)
    return img


def deskew(img: np.ndarray) -> np.ndarray:
    """Rotate so text lines are horizontal; skips tiny or implausibly large angles."""
    pts = cv2.findNonZero(_ink(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
    if pts is None or len(pts) < 50:
        return img
    angle = cv2.minAreaRect(pts)[2]
    angle = angle - 90 if angle > 45 else angle  # normalise to (-45, 45]
    if abs(angle) < 0.3 or abs(angle) > MAX_DESKEW_DEG:
        return img
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(
        img,
        m,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def preprocess_page(
    page: int, data: bytes, cfg: GateConfig = DEFAULT_GATE
) -> tuple[PreprocessedPage | None, RetakeReason | None]:
    """Gate on the raw capture, then crop + deskew. Exactly one of the two results is set."""
    img = decode(data)
    if img is None:
        return None, RetakeReason.NOT_A_DOCUMENT
    raw = measure(img)
    reason = decide(raw, cfg)
    if reason is not None:
        return None, reason
    out = deskew(crop_document(img))
    ok, png = cv2.imencode(".png", out)
    if not ok:
        raise RuntimeError("encode_failed")
    return PreprocessedPage(page, png.tobytes(), quality_score(raw, cfg), raw), None
