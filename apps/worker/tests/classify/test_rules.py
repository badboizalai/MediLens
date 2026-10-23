import pytest
from medilens_worker.classify.page_types import PageType
from medilens_worker.classify.rules import LLM_FALLBACK_THRESHOLD, classify_text

CASES = [
    ("GIẤY RA VIỆN\nNgày ra viện: 2024-01-02", PageType.DISCHARGE_SUMMARY),
    ("Discharge summary\nDate of discharge: 2024-01-02", PageType.DISCHARGE_SUMMARY),
    ("PHIẾU KHÁM BỆNH\nHọ tên: Nguyễn Văn Mẫu\nNgày khám: 2024-01-02", PageType.OUTPATIENT_FORM),
    ("KẾT QUẢ XÉT NGHIỆM\nGlucose 5.4 mmol/L\nKhoảng tham chiếu 3.9-6.1", PageType.LAB_RESULT),
    ("Laboratory report\nLDL 120 mg/dL reference range <100", PageType.LAB_RESULT),
    ("BÁO CÁO GIẢI PHẪU BỆNH\nSinh thiết", PageType.PATHOLOGY_REPORT),
    ("Pathology report: biopsy of left breast", PageType.PATHOLOGY_REPORT),
    ("KẾT QUẢ CHẨN ĐOÁN HÌNH ẢNH\nChụp X-quang ngực thẳng", PageType.IMAGING_REPORT),
    ("Radiology report: CT scan chest", PageType.IMAGING_REPORT),
    ("Khoa Răng Hàm Mặt\nRăng 14: sâu răng", PageType.DENTAL_RECORD),
    ("Dental Department\nTooth 21: filling", PageType.DENTAL_RECORD),
    ("ĐƠN THUỐC\n1. Thuốc A viên", PageType.PRESCRIPTION),
    ("Prescription\nTablet x 10", PageType.PRESCRIPTION),
    ("PHIẾU CHỈ ĐỊNH CẬN LÂM SÀNG", PageType.ORDER_FORM),
    ("Lab order form", PageType.ORDER_FORM),
]


@pytest.mark.parametrize(("text", "expected"), CASES)
def test_types(text, expected):
    page_type, conf = classify_text(text)
    assert page_type is expected
    assert conf >= LLM_FALLBACK_THRESHOLD


def test_title_beats_stray_mention():
    # dev-split failures: a stray "xet nghiem" / "rang 16" line must not outvote the page title
    assert (
        classify_text("TOA THUỐC\nHọ tên: Nguyen Van Test\nKết quả xét nghiệm máu: bình thường")[0]
        is PageType.PRESCRIPTION
    )
    assert (
        classify_text("PHIẾU SIÊU ÂM\nHọ tên: Nguyen Van Test\nKết quả xét nghiệm máu")[0]
        is PageType.IMAGING_REPORT
    )
    assert (
        classify_text("PHIẾU CHỈ ĐỊNH\nHọ tên: Nguyen Van Test\nRăng 16 đã khám")[0]
        is PageType.ORDER_FORM
    )


@pytest.mark.parametrize("text", ["GIẤY HẸN TÁI KHÁM", "Insurance Card Copy", "Consent Form"])
def test_other(text):
    assert classify_text(text)[0] is PageType.OTHER


def test_diacritics_insensitive():
    assert classify_text("GIAY RA VIEN")[0] is PageType.DISCHARGE_SUMMARY
    assert classify_text("đơn thuốc")[0] is PageType.PRESCRIPTION


@pytest.mark.parametrize("text", ["", "   ", "lorem ipsum 123"])
def test_unknown_when_no_rule_fires(text):
    page_type, conf = classify_text(text)
    assert page_type is PageType.UNKNOWN
    assert conf < LLM_FALLBACK_THRESHOLD


def test_mixed_signals_lower_confidence():
    _, mixed = classify_text("PHIẾU KHÁM BỆNH\nKết quả xét nghiệm")
    _, clean = classify_text("PHIẾU KHÁM BỆNH")
    assert mixed < clean
