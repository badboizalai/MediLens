"""Synthetic record content: ground truth (schema-valid) plus the text lines to render.

Everything here is fictional. No treatment, dosing or advice text (BR-042).
"""

from __future__ import annotations

import random
from datetime import date, timedelta

FAMILY = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"]
GIVEN = ["Test", "Mẫu", "Giả", "Thử Nghiệm", "Demo"]

FACILITY = {
    "vi": "Bệnh viện Thử Nghiệm",
    "en": "Benh vien Thu Nghiem (Test Hospital)",
}
DEPARTMENT = {
    "dental": {"vi": "Khoa Răng Hàm Mặt", "en": "Dental Department"},
    "cardiology": {"vi": "Khoa Tim mạch", "en": "Cardiology Department"},
    "oncology": {"vi": "Khoa Ung bướu", "en": "Oncology Department"},
}

LABELS = {
    "vi": {
        "title": "PHIẾU KHÁM BỆNH (DỮ LIỆU TỔNG HỢP - KHÔNG PHẢI HỒ SƠ THẬT)",
        "patient": "Họ tên",
        "birth": "Năm sinh",
        "sex": "Giới",
        "date": "Ngày khám",
        "dept": "Khoa",
        "tooth": "Răng",
        "surf": "mặt",
        "dx": "Chẩn đoán",
        "obs": "Xét nghiệm",
        "proc": "Thăm dò",
        "primary": "U nguyên phát",
        "histology": "Mô học",
        "size": "Kích thước",
        "grade": "Độ mô học",
        "tnm": "TNM",
        "stage": "Giai đoạn",
        "node": "Hạch",
        "mets": "Di căn",
        "confirmed": "đã xác nhận",
        "suspected": "nghi ngờ",
        "involved": "có xâm lấn",
        "not_involved": "không xâm lấn",
        "history": "Tiền sử",
        "ref": "tham chiếu",
        "male": "Nam",
        "female": "Nữ",
    },
    "en": {
        "title": "MEDICAL RECORD (SYNTHETIC DATA - NOT A REAL RECORD)",
        "patient": "Name",
        "birth": "Birth year",
        "sex": "Sex",
        "date": "Visit date",
        "dept": "Department",
        "tooth": "Tooth",
        "surf": "surface",
        "dx": "Diagnosis",
        "obs": "Lab results",
        "proc": "Studies",
        "primary": "Primary tumour",
        "histology": "Histology",
        "size": "Size",
        "grade": "Grade",
        "tnm": "TNM",
        "stage": "Stage",
        "node": "Node",
        "mets": "Metastasis",
        "confirmed": "confirmed",
        "suspected": "suspected",
        "involved": "involved",
        "not_involved": "not involved",
        "history": "History",
        "ref": "ref",
        "male": "Male",
        "female": "Female",
    },
}

# --- Dental -----------------------------------------------------------------
FDI_PERMANENT = [f"{q}{n}" for q in (1, 2, 3, 4) for n in range(1, 9)]
TOOTH_CONDITIONS = {
    "caries": ("sâu răng", "caries"),
    "missing": ("mất răng", "missing"),
    "filling": ("trám", "filling"),
    "crown": ("mão răng", "crown"),
    "implant": ("implant", "implant"),
    "root_canal": ("đã nội nha", "root canal treated"),
    "pulpitis": ("viêm tủy", "pulpitis"),
    "periapical_lesion": ("tổn thương quanh chóp", "periapical lesion"),
    "impacted": ("răng ngầm", "impacted"),
    "fracture": ("nứt/gãy răng", "fracture"),
}
SURFACE_CONDITIONS = {"caries", "filling"}
SEVERITIES = ["monitor", "mild", "moderate", "severe"]
SEVERITY_TEXT = {
    "vi": {"monitor": "theo dõi", "mild": "nhẹ", "moderate": "vừa", "severe": "nặng"},
    "en": {"monitor": "monitor", "mild": "mild", "moderate": "moderate", "severe": "severe"},
}
PERIO = [("viêm lợi", "gingivitis"), ("túi nha chu", "periodontal pocket")]

# --- Cardiology -------------------------------------------------------------
# (ICD-10, vi, en, site vi, site en, laterality)
CARDIO_DX = [
    ("I10", "Tăng huyết áp vô căn", "Essential hypertension", "Hệ tuần hoàn", "Circulatory"),
    (
        "I25.1",
        "Bệnh mạch vành xơ vữa",
        "Atherosclerotic heart disease",
        "Động mạch vành",
        "Coronary artery",
    ),
    ("I48.9", "Rung nhĩ", "Atrial fibrillation", "Tâm nhĩ", "Atrium"),
    ("I50.9", "Suy tim", "Heart failure", "Tim", "Heart"),
    ("I20.9", "Cơn đau thắt ngực", "Angina pectoris", "Tim", "Heart"),
    ("I34.0", "Hở van hai lá", "Mitral regurgitation", "Van hai lá", "Mitral valve"),
    ("I35.0", "Hẹp van động mạch chủ", "Aortic stenosis", "Van động mạch chủ", "Aortic valve"),
]
# (name vi, name en, LOINC, unit, lo, hi, ref range)
CARDIO_OBS = [
    ("Huyết áp tâm thu", "Systolic blood pressure", "8480-6", "mmHg", 110, 170, "90-120"),
    ("Huyết áp tâm trương", "Diastolic blood pressure", "8462-4", "mmHg", 60, 100, "60-80"),
    ("Nhịp tim", "Heart rate", "8867-4", "/min", 55, 110, "60-100"),
    ("Troponin I", "Troponin I", "10839-9", "ng/mL", 0.01, 0.08, "<0.04"),
    ("Cholesterol toàn phần", "Total cholesterol", "2093-3", "mg/dL", 140, 280, "<200"),
    ("LDL-C", "LDL cholesterol", "13457-7", "mg/dL", 70, 190, "<100"),
    ("Phân suất tống máu (EF)", "Ejection fraction", "10230-1", "%", 30, 65, "55-70"),
]
CARDIO_PROCS = [
    ("Điện tâm đồ", "Electrocardiogram"),
    ("Siêu âm tim", "Echocardiography"),
    ("Chụp động mạch vành", "Coronary angiography"),
    ("Holter điện tâm đồ", "Holter monitoring"),
]

# --- Oncology ---------------------------------------------------------------
# (site vi, site en, ICD-10, laterality?, histology vi, histology en, mets sites)
ONCO_PRIMARY = [
    ("Vú", "Breast", "C50.9", True, "Ung thư biểu mô ống xâm nhập", "Invasive ductal carcinoma"),
    ("Đại tràng", "Colon", "C18.9", False, "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    (
        "Phổi (thùy trên)",
        "Lung (upper lobe)",
        "C34.1",
        True,
        "Ung thư biểu mô tuyến",
        "Adenocarcinoma",
    ),
    ("Tiền liệt tuyến", "Prostate", "C61", False, "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Tuyến giáp", "Thyroid", "C73", False, "Ung thư biểu mô nhú", "Papillary carcinoma"),
]
# (T, N, M, stage)
TNM_STAGES = [
    ("T1", "N0", "M0", "IA"),
    ("T2", "N0", "M0", "IIA"),
    ("T2", "N1", "M0", "IIB"),
    ("T3", "N1", "M0", "IIIA"),
    ("T2", "N0", "M1", "IV"),
    ("T3", "N1", "M1", "IV"),
]
NODE_STATIONS = ["Hạch nách", "Hạch cạnh khí quản", "Hạch trung thất", "Hạch chậu"]
NODE_STATIONS_EN = ["Axillary", "Paratracheal", "Mediastinal", "Iliac"]
MET_SITES = [("Gan", "Liver"), ("Phổi", "Lung"), ("Xương", "Bone"), ("Não", "Brain")]
TREATMENT_HISTORY = [
    ("surgery", "Phẫu thuật", "Surgery"),
    ("radiotherapy", "Xạ trị", "Radiotherapy"),
    ("chemotherapy", "Hóa trị", "Chemotherapy"),
]
LATERALITY_TEXT = {
    "vi": {"left": "trái", "right": "phải", "midline": "", "unknown": ""},
    "en": {"left": "left", "right": "right", "midline": "", "unknown": ""},
}


def make_patient(rng: random.Random) -> dict:
    female = rng.random() < 0.5
    return {
        "name": f"{rng.choice(FAMILY)} {'Thị' if female else 'Văn'} {rng.choice(GIVEN)}",
        "birth_year": rng.randint(1900, 1950),
        "sex": "female" if female else "male",
    }


def _f(value, quote: str, conf: float = 1.0) -> dict:
    """Schema 'Field' wrapper; source is page 1 with the exact rendered quote."""
    return {"value": value, "confidence": conf, "source": {"page": 1, "quote": quote}}


def _date(rng: random.Random) -> date:
    return date(2024, 1, 1) + timedelta(days=rng.randint(0, 700))


def _encounter(rng: random.Random, unit: str, lang: str, lines: list[str]) -> dict:
    lab = LABELS[lang]
    d = _date(rng).isoformat()
    dept = DEPARTMENT[unit][lang]
    fac = FACILITY[lang]
    lines.append(f"{fac}")
    lines.append(f"{lab['dept']}: {dept}")
    lines.append(f"{lab['date']}: {d}")
    return {"date": _f(d, d), "facility": _f(fac, fac), "department": _f(dept, dept)}


def build_dental(rng: random.Random, lang: str, lines: list[str]) -> dict:
    lab = LABELS[lang]
    enc = _encounter(rng, "dental", lang, lines)
    teeth = []
    for fdi in sorted(rng.sample(FDI_PERMANENT, rng.randint(2, 5))):
        cond = rng.choice(list(TOOTH_CONDITIONS))
        vi, en = TOOTH_CONDITIONS[cond]
        surfaces = (
            sorted(rng.sample("OMDBL", rng.randint(1, 2))) if cond in SURFACE_CONDITIONS else []
        )
        sev = (
            rng.choice(SEVERITIES) if cond in {"caries", "pulpitis", "periapical_lesion"} else None
        )
        text = f"{lab['tooth']} {fdi}: {vi if lang == 'vi' else en}"
        if surfaces:
            text += f" ({lab['surf']} {''.join(surfaces)})"
        if sev:
            text += f" - {SEVERITY_TEXT[lang][sev]}"
        lines.append(text)
        item = {"fdi": _f(fdi, f"{lab['tooth']} {fdi}"), "condition": cond}
        if surfaces:
            item["surfaces"] = surfaces
        if sev:
            item["severity"] = sev
        teeth.append(item)
    out = {"encounter": enc, "dentition": "permanent", "teeth": teeth}
    if rng.random() < 0.3:
        q = rng.randint(1, 4)
        vi, en = rng.choice(PERIO)
        txt = f"{vi if lang == 'vi' else en} (Q{q})"
        lines.append(txt)
        out["periodontal"] = [{"quadrant": q, "condition": _f(vi if lang == "vi" else en, txt)}]
    return out


def build_cardiology(rng: random.Random, lang: str, lines: list[str]) -> dict:
    lab = LABELS[lang]
    enc = _encounter(rng, "cardiology", lang, lines)
    diagnoses = []
    lines.append(f"{lab['dx']}:")
    for code, vi, en, site_vi, site_en in rng.sample(CARDIO_DX, rng.randint(1, 3)):
        name = vi if lang == "vi" else en
        site = site_vi if lang == "vi" else site_en
        txt = f"- {name} ({code})"
        lines.append(txt)
        diagnoses.append(
            {
                "text": _f(name, name),
                "icd10_candidates": [{"code": code, "score": 1.0}],
                "site": _f(site, site),
                "laterality": "unknown",
                "severity": None,
            }
        )
    observations = []
    lines.append(f"{lab['obs']}:")
    for name_vi, name_en, loinc, unit, lo, hi, ref in rng.sample(CARDIO_OBS, rng.randint(3, 5)):
        name = name_vi if lang == "vi" else name_en
        val = round(rng.uniform(lo, hi), 2 if hi < 1 else (1 if hi < 100 else 0))
        txt = f"{name}: {val:g} {unit}  ({lab['ref']} {ref})"
        lines.append(txt)
        observations.append(
            {
                "name": _f(name, name),
                "value": {**_f(val, f"{val:g} {unit}"), "unit": unit},
                "reference_range": _f(ref, ref),
                "loinc_hint": loinc,
            }
        )
    out = {"encounter": enc, "diagnoses": diagnoses, "observations": observations}
    procs = rng.sample(CARDIO_PROCS, rng.randint(0, 2))
    if procs:
        lines.append(f"{lab['proc']}:")
        out["procedures"] = []
        for vi, en in procs:
            p = vi if lang == "vi" else en
            lines.append(f"- {p}")
            out["procedures"].append(_f(p, p))
    return out


def build_oncology(rng: random.Random, lang: str, lines: list[str]) -> dict:
    lab = LABELS[lang]
    vi = lang == "vi"
    enc = _encounter(rng, "oncology", lang, lines)
    site_vi, site_en, icd, lateral, hist_vi, hist_en = rng.choice(ONCO_PRIMARY)
    site = site_vi if vi else site_en
    side = rng.choice(["left", "right"]) if lateral else "midline"
    side_txt = LATERALITY_TEXT[lang][side]
    size = rng.randint(8, 60)
    grade = f"G{rng.randint(1, 3)}"
    hist = hist_vi if vi else hist_en
    t, n, m, stage = rng.choice(TNM_STAGES)
    lines.append(f"{lab['primary']}: {site} {side_txt} ({icd})".replace("  ", " "))
    lines.append(f"{lab['histology']}: {hist}")
    lines.append(f"{lab['size']}: {size} mm; {lab['grade']}: {grade}")
    lines.append(f"{lab['tnm']}: {t} {n} {m} (AJCC 8); {lab['stage']}: {stage}")
    out = {
        "encounter": enc,
        "primary": {
            "site": _f(site, site),
            "laterality": side,
            "histology": _f(hist, hist),
            "size_mm": {**_f(size, f"{size} mm"), "unit": "mm"},
            "grade": _f(grade, grade),
        },
        "tnm": {
            "t": _f(t, t),
            "n": _f(n, n),
            "m": _f(m, m),
            "stage": _f(stage, stage),
            "edition": "AJCC 8",
        },
        "nodes": [],
        "metastases": [],
        "treatments": [],
    }
    if n != "N0":
        i = rng.randrange(len(NODE_STATIONS))
        st = NODE_STATIONS[i] if vi else NODE_STATIONS_EN[i]
        lines.append(f"{lab['node']}: {st} - {lab['involved']}")
        out["nodes"].append({"station": _f(st, st), "involved": True})
    if m == "M1":
        for ms_vi, ms_en in rng.sample(MET_SITES, rng.randint(1, 2)):
            ms = ms_vi if vi else ms_en
            stated = rng.choice(["confirmed", "suspected"])
            lines.append(f"{lab['mets']}: {ms} ({lab[stated]})")
            out["metastases"].append({"site": _f(ms, ms), "stated_as": stated})
    if rng.random() < 0.5:
        ttype, t_vi, t_en = rng.choice(TREATMENT_HISTORY)
        tdate = (_date(rng) - timedelta(days=rng.randint(60, 300))).isoformat()
        lines.append(f"{lab['history']}: {t_vi if vi else t_en} {tdate}")
        out["treatments"].append({"type": ttype, "date": _f(tdate, tdate)})
    return out


BUILDERS = {"dental": build_dental, "cardiology": build_cardiology, "oncology": build_oncology}
