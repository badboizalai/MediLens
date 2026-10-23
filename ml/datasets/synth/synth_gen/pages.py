"""Text-level synthetic pages for the 9 page types (classifier eval, S6-T54c). 100 % fictional.

Each page = title variant + header + type body + optional distractor line from another type
(real pages mention labs/CT/teeth in passing) + footer. No treatment/dosing/advice (BR-042).
Split alternates by index: `dev` for rule tuning, `test` held out.
"""

from __future__ import annotations

import random

FOOTER = "SYNTHETIC - TEST ONLY"
TYPES = ["discharge_summary", "outpatient_form", "lab_result", "pathology_report",
         "imaging_report", "dental_record", "prescription", "order_form", "other"]  # fmt: skip
PER_TYPE = 40  # 20 dev + 20 test

TITLES = {
    "discharge_summary": [
        "GIẤY RA VIỆN",
        "TÓM TẮT BỆNH ÁN",
        "Discharge Summary",
        "DISCHARGE SUMMARY",
    ],
    "outpatient_form": [
        "PHIẾU KHÁM BỆNH",
        "PHIẾU KHÁM NGOẠI TRÚ",
        "Outpatient Visit Form",
        "OUTPATIENT RECORD",
    ],  # fmt: skip
    "lab_result": ["KẾT QUẢ XÉT NGHIỆM", "PHIẾU XÉT NGHIỆM", "Laboratory Report", "Lab Results"],
    "pathology_report": [
        "KẾT QUẢ GIẢI PHẪU BỆNH",
        "PHIẾU MÔ BỆNH HỌC",
        "Pathology Report",
        "Histology / Pathology",
    ],  # fmt: skip
    "imaging_report": [
        "KẾT QUẢ CHẨN ĐOÁN HÌNH ẢNH",
        "PHIẾU SIÊU ÂM",
        "Imaging Report",
        "Radiology Report",
    ],  # fmt: skip
    "dental_record": ["PHIẾU KHÁM RĂNG HÀM MẶT", "SƠ ĐỒ RĂNG", "Dental Record", "Odontogram"],
    "prescription": ["ĐƠN THUỐC", "TOA THUỐC", "Prescription", "PRESCRIPTION"],
    "order_form": ["PHIẾU CHỈ ĐỊNH", "PHIẾU YÊU CẦU XÉT NGHIỆM", "Order Form", "Test Requisition"],
    "other": [
        "GIẤY CHỨNG NHẬN",
        "GIẤY HẸN TÁI KHÁM",
        "Appointment Slip",
        "Insurance Card Copy",
        "Consent Form",
    ],  # fmt: skip
}
BODY = {
    "discharge_summary": [
        "Ngày ra viện: {d}",
        "Date of discharge: {d}",
        "Ngày vào viện: {d}",
        "Tình trạng ra viện: ổn định",
        "Condition at discharge: stable",
    ],  # fmt: skip
    "outpatient_form": [
        "Ngày khám: {d}",
        "Visit date: {d}",
        "Lý do khám: đau đầu nhẹ",
        "Chief complaint: mild cough",
        "Khoa: Nội tổng quát",
    ],  # fmt: skip
    "lab_result": [
        "Glucose {n} mmol/L  (khoảng tham chiếu 3.9-6.1)",
        "LDL {n} mg/dL reference range <100",
        "Hemoglobin {n} g/L",
        "ALT {n} U/L",
        "Ngày lấy mẫu: {d}",
    ],  # fmt: skip
    "pathology_report": [
        "Mẫu bệnh phẩm: sinh thiết da",
        "Specimen: biopsy of left breast",
        "Mô tả vi thể: mô tuyến",
        "Microscopic: glandular tissue",
        "Grade: {g}",
    ],  # fmt: skip
    "imaging_report": [
        "Chụp X-quang ngực thẳng",
        "CT scan abdomen",
        "MRI brain without contrast",
        "Siêu âm bụng tổng quát",
        "Findings: no acute abnormality",
    ],  # fmt: skip
    "dental_record": [
        "Răng 1{t}: sâu mặt nhai",
        "Tooth 2{t}: filling",
        "Răng 3{t}: đã trám",
        "Tooth 4{t}: extracted",
        "Cao răng độ {g}",
    ],  # fmt: skip
    "prescription": [
        "1. Thuốc A 500mg  {n} viên",
        "2. Thuốc B  {n} viên",
        "Tablet x {n}",
        "Capsule C x {n}",
        "Ngày kê đơn: {d}",
    ],  # fmt: skip
    "order_form": [
        "Chỉ định: công thức máu",
        "Requested: chest X-ray",
        "Bác sĩ chỉ định: Dr. Test",
        "Ordering clinician: Dr. Demo",
        "Ngày chỉ định: {d}",
    ],  # fmt: skip
    "other": [
        "Ngày: {d}",
        "Date: {d}",
        "Số thẻ: 0000{n}",
        "Ghi chú: mang theo giấy tờ",
        "Please bring this slip",
    ],  # fmt: skip
}
# One stray line from an unrelated type, e.g. a discharge note that mentions a CT.
DISTRACT = ["Đã chụp CT ngực", "Kết quả xét nghiệm máu: bình thường", "Siêu âm: không bất thường",
            "Răng 16 đã khám", "Biopsy not required"]  # fmt: skip


def _page(kind: str, rng: random.Random) -> str:
    d = f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
    fill = {"d": d, "n": rng.randint(2, 99), "g": rng.randint(1, 3), "t": rng.randint(1, 8)}
    lines = [
        rng.choice(TITLES[kind]),
        rng.choice(["Họ tên: Nguyen Van Test", "Name: Nguyen Van Test"]) + ", birth_year 1900",
        *(b.format(**fill) for b in rng.sample(BODY[kind], rng.randint(2, 4))),
    ]
    if rng.random() < 0.3:
        lines.insert(rng.randint(2, len(lines)), rng.choice(DISTRACT))
    return "\n".join([*lines, FOOTER])


def generate_pages(seed: int, per_type: int = PER_TYPE) -> list[dict]:
    """Deterministic labelled pages: [{id, label, split, text}], per_type per type, half dev/test."""
    rng = random.Random(seed)  # noqa: S311 - deterministic synthetic data
    return [
        {
            "id": f"pg-{kind}-{i:03d}",
            "label": kind,
            "split": "dev" if i % 2 == 0 else "test",
            "text": _page(kind, rng),
        }  # fmt: skip
        for kind in TYPES
        for i in range(per_type)
    ]
