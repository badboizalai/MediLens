"""Tests for claims_lint BR-042 boundary rules (run: pytest this folder)."""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "claims_lint", pathlib.Path(__file__).with_name("claims_lint.py")
)
cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cl)


def levels(tmp_path, text):
    f = tmp_path / "t.md"
    f.write_text(text, encoding="utf-8")
    return {x["level"] for x in cl.scan(str(f), set())}


BLOCKED = [
    # AI reading / interpreting scans
    "AI đọc phim X-quang giúp bạn",
    "AI doc phim X-quang giup ban",
    "Máy phân tích ảnh CT tự động",
    "May phan tich anh CT tu dong",
    "AI reads your scan in seconds",
    "Our AI interprets X-rays",
    "Automatic tumour measurement on CT",
    "Đo kích thước khối u tự động",
    "Do kich thuoc khoi u tu dong",
    # detection
    "Phát hiện sớm tổn thương trên ảnh",
    "Phat hien som ton thuong tren anh",
    "Phát hiện tổn thương trên CT",
    "Phat hien ton thuong tren CT",
    "App finds lesions on CT",
    "Detects lesions in your scan",
    # risk score
    "Điểm nguy cơ của bạn là cao",
    "Diem nguy co cua ban",
    "Your risk score is high",
    "Your risk of stroke is 40%",
    "Nguy cơ mắc bệnh tim 40%",
    "Nguy co mac benh tim 40%",
    # symptom checker
    "Triệu chứng này có thể là bệnh tim",
    "Trieu chung nay co the la benh tim",
    "Try our symptom checker",
    "Your symptoms may mean something serious",
    # alerts on worsening
    "Cảnh báo chỉ số xấu đi",
    "Canh bao chi so xau di",
    "Cảnh báo xu hướng nguy hiểm",
    "Canh bao xu huong nguy hiem",
    "Cảnh báo bệnh nặng thêm",
    "Canh bao benh nang them",
    "We alert you when your results get worse",
    "Enable trend alerts",
    # colour inference
    "Màu đỏ nghĩa là nguy hiểm",
    "Mau do nghia la nguy hiem",
    "Red means dangerous",
]

REVIEWED = [
    "An toàn cho bệnh nhân",
    "An toan cho benh nhan",
    "Đạt chuẩn y tế",
    "Dat chuan y te",
    "Medical-grade viewer",
    "Patient-safe design",
    "ISO-certified process",
]

BENIGN = [
    "MediLens shows findings written in your records.",
    "Hiển thị các phát hiện đã ghi trong hồ sơ của bạn.",
    "Please read the scan report with your doctor.",
    "Bạn có thể xem ảnh CT cùng bác sĩ.",
    "The reference range is printed by the lab.",
]


@pytest.mark.parametrize("text", BLOCKED)
def test_blocked(tmp_path, text):
    assert "BLOCK" in levels(tmp_path, text)


@pytest.mark.parametrize("text", REVIEWED)
def test_review(tmp_path, text):
    assert levels(tmp_path, text) == {"REVIEW"}


@pytest.mark.parametrize("text", BENIGN)
def test_benign(tmp_path, text):
    assert levels(tmp_path, text) == set()


@pytest.mark.parametrize("text", BLOCKED)
def test_claims_ok_skips(tmp_path, text):
    assert levels(tmp_path, f"{text} <!-- claims-ok -->") == set()


def test_negated_risk_scoring_passes(tmp_path):
    assert levels(tmp_path, "Không chấm điểm nguy cơ") == set()
    assert levels(tmp_path, "Khong cham diem nguy co") == set()
