"""Rules page classifier: weighted VI/EN keyword scoring over diacritics-stripped text."""

from __future__ import annotations

import re
import unicodedata

from medilens_worker.classify.page_types import PageType

# Below this confidence the caller should ask the LlmClassifier (Tier S).
LLM_FALLBACK_THRESHOLD = 0.5
_SATURATION = 4.0  # total weight at which evidence counts as fully strong

# Patterns are matched on lowercase text with diacritics removed (and đ -> d). Each counts once.
_RULES: dict[PageType, list[tuple[str, float]]] = {
    PageType.DISCHARGE_SUMMARY: [
        (r"giay ra vien|discharge summary", 3),
        (r"tom tat benh an|ngay ra vien|date of discharge|discharge date", 2),
    ],
    PageType.OUTPATIENT_FORM: [
        (r"phieu kham benh|outpatient|kham ngoai tru", 3),
        (r"ngay kham|visit date", 2),
        (r"medical record", 1),
    ],
    PageType.LAB_RESULT: [
        (r"ket qua xet nghiem|phieu xet nghiem|laboratory (report|results?)|lab report", 3),
        (r"khoang tham chieu|reference range", 2),
        (r"xet nghiem|lab results?|\b(mg/dl|mmol/l|g/l|u/l)\b", 1),
    ],
    PageType.PATHOLOGY_REPORT: [
        (r"giai phau benh|pathology|mo benh hoc", 3),
        (r"sinh thiet|biops|histolog|mo hoc", 1),
    ],
    PageType.IMAGING_REPORT: [
        (r"chan doan hinh anh|imaging report|radiology", 3),
        (r"phieu sieu am|ket qua sieu am", 3),
        (r"x-?\s?quang|x-ray|\bct\b|\bmri\b|sieu am|ultrasound", 1),
    ],
    PageType.DENTAL_RECORD: [
        (r"rang ham mat|dental|odontogram|so do rang", 3),
        (r"\brang \d\d\b|\btooth \d\d\b", 3),
        (r"sau rang|tram rang", 1),
    ],
    PageType.PRESCRIPTION: [
        (r"don thuoc|toa thuoc|prescription", 3),
        (r"\bvien\b|tablet|capsule", 1),
    ],
    PageType.ORDER_FORM: [
        (r"phieu chi dinh|phieu yeu cau|order form|requisition|lab order", 3),
    ],
    PageType.OTHER: [
        (r"giay chung nhan|giay hen|appointment|the bao hiem|insurance|consent|cam ket", 3),
    ],
}
_TITLE_LINES = 2  # a strong (weight >= 3) match in the first lines is the page title:
_TITLE_BONUS = 2  # it outranks a stray mention further down (e.g. "xet nghiem mau: binh thuong")
_COMPILED = {t: [(re.compile(p), w) for p, w in rs] for t, rs in _RULES.items()}


def normalize(text: str) -> str:
    stripped = "".join(
        c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn"
    )
    return stripped.replace("đ", "d")


def classify_text(text: str) -> tuple[PageType, float]:
    """Return (page type, confidence 0..1); (UNKNOWN, 0.0) when no rule fires."""
    norm = normalize(text)
    head = "\n".join([ln for ln in norm.splitlines() if ln.strip()][:_TITLE_LINES])
    scores = {
        t: sum(
            w + (_TITLE_BONUS if w >= 3 and rx.search(head) else 0)
            for rx, w in rs
            if rx.search(norm)
        )
        for t, rs in _COMPILED.items()
    }
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    (best, top), (_, second) = ranked[0], ranked[1]
    if top == 0:
        return PageType.UNKNOWN, 0.0
    return best, round(top / (top + second) * min(top, _SATURATION) / _SATURATION, 3)
