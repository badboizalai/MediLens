"""OpenCV tests: skipped unless the `ocr` extra is installed. Synthetic images only."""

from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from medilens_worker.ocr import service  # noqa: E402
from medilens_worker.ocr.preprocess import crop_document, measure, preprocess_page  # noqa: E402
from medilens_worker.ocr.service import InMemoryPageStore  # noqa: E402
from medilens_worker.ocr.types import RetakeReason, RetakeRequired  # noqa: E402

GOLDEN = Path(__file__).resolve().parents[4] / "ml" / "eval" / "golden-v1" / "images"


def _text_page(w=1000, h=1400, angle=0.0):
    img = np.full((h, w, 3), 255, np.uint8)
    for i in range(30):
        cv2.putText(img, f"Line {i} abc XYZ 0123", (60, 80 + 40 * i), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0, 0, 0), 2)  # fmt: skip
    if angle:
        m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        img = cv2.warpAffine(img, m, (w, h), borderValue=(255, 255, 255))
    return img


def _enc(img):
    return cv2.imencode(".png", img)[1].tobytes()


def test_sharp_page_passes():
    page, reason = preprocess_page(1, _enc(_text_page()))
    assert reason is None and page is not None and 0 < page.quality <= 1


def test_blurry_page_rejected():
    blurred = cv2.GaussianBlur(_text_page(), (0, 0), 8)
    assert preprocess_page(1, _enc(blurred))[1] == RetakeReason.BLURRY


def test_dark_page_rejected():
    dark = (_text_page() * 0.1).astype(np.uint8)
    assert preprocess_page(1, _enc(dark))[1] == RetakeReason.TOO_DARK


def test_blank_and_garbage_rejected():
    blank = np.full((1000, 1000, 3), 200, np.uint8)
    assert preprocess_page(1, _enc(blank))[1] == RetakeReason.NOT_A_DOCUMENT
    assert preprocess_page(1, b"not an image")[1] == RetakeReason.NOT_A_DOCUMENT


def test_deskew_reduces_tilt():
    tilted = _text_page(angle=6.0)
    page, _ = preprocess_page(1, _enc(tilted))
    assert page is not None
    out = cv2.imdecode(np.frombuffer(page.image, np.uint8), cv2.IMREAD_COLOR)

    # horizontal text => row-projection variance rises after straightening
    def sharp_rows(a):
        return np.var((255 - cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)).sum(axis=1))

    assert sharp_rows(out) > sharp_rows(tilted)


def test_perspective_crop_finds_page_on_desk():
    desk = np.full((1200, 1600, 3), 40, np.uint8)
    page = _text_page(800, 1000)
    src = np.float32([[0, 0], [799, 0], [799, 999], [0, 999]])
    dst = np.float32([[300, 120], [1250, 180], [1200, 1100], [250, 1050]])
    warp = cv2.warpPerspective(page, cv2.getPerspectiveTransform(src, dst), (1600, 1200))
    mask = cv2.warpPerspective(np.full((1000, 800), 255, np.uint8),
                               cv2.getPerspectiveTransform(src, dst), (1600, 1200))  # fmt: skip
    desk[mask > 0] = warp[mask > 0]
    out, reason = preprocess_page(1, _enc(desk))
    assert reason is None and out is not None
    img = cv2.imdecode(np.frombuffer(out.image, np.uint8), cv2.IMREAD_COLOR)
    assert img.shape[0] < 1200 and img.mean() > 150  # desk cropped away


def _on_desk(bg, dst, size=(1600, 1200), page=None):
    page = _text_page(800, 1000) if page is None else page
    h, w = page.shape[:2]
    src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    m = cv2.getPerspectiveTransform(src, np.float32(dst))
    desk = np.full((size[1], size[0], 3), bg, np.uint8)
    inside = cv2.warpPerspective(np.full((h, w), 255, np.uint8), m, size) > 0
    desk[inside] = cv2.warpPerspective(page, m, size)[inside]
    return desk


MILD = [[200, 100], [1000, 130], [980, 1130], [220, 1100]]  # ~800x1000 page, mild keystone


@pytest.mark.parametrize("bg", [40, 225])  # dark desk (Otsu) and low-contrast desk (Canny)
def test_crop_document_warps_to_upright_page(bg):
    out = crop_document(_on_desk(bg, MILD))
    h, w = out.shape[:2]
    assert 0.7 < w / h < 0.95  # page is 0.8 wide:high
    gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    for y, x in [(8, 8), (8, w - 9), (h - 9, 8), (h - 9, w - 9)]:  # no desk left in corners
        assert gray[y - 4 : y + 5, x - 4 : x + 5].min() > 200
    # axis-aligned: text rows project sharply
    assert np.var((255 - gray).sum(axis=1)) > 0


def test_crop_document_falls_back_when_no_page():
    flat = np.full((600, 800, 3), 128, np.uint8)
    noise = np.random.default_rng(0).integers(0, 255, (600, 800, 3), dtype=np.uint8)
    assert crop_document(flat) is flat
    assert crop_document(noise) is noise


def test_service_raises_retake_and_records_code():
    bad = _enc(cv2.GaussianBlur(_text_page(), (0, 0), 8))
    store = InMemoryPageStore({"d1": [_enc(_text_page()), bad]})
    with pytest.raises(RetakeRequired) as e:
        service.run_preprocess("d1", store)
    assert e.value.page == 2 and store.retakes["d1"] == (2, RetakeReason.BLURRY)
    assert "d1" not in store.pre


@pytest.mark.skipif(not GOLDEN.exists(), reason="golden-v1 images not present")
def test_golden_v1_clean_pages_pass_gate():
    files = sorted(GOLDEN.glob("*_clean.jpg"))[:3]
    assert files
    for f in files:
        m = measure(cv2.imread(str(f)))
        page, reason = preprocess_page(1, f.read_bytes())
        assert reason is None, (f.name, m)
        assert page is not None
