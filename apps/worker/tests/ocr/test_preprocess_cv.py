"""OpenCV tests: skipped unless the `ocr` extra is installed. Synthetic images only."""

from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from medilens_worker.ocr import service  # noqa: E402
from medilens_worker.ocr.preprocess import measure, preprocess_page  # noqa: E402
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
