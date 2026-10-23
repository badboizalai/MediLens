"""golden-v2: 200 synthetic text documents per Unit (dental, cardiology, oncology) = 600.

    python -m synth_gen.golden_v2 --out ../../eval/golden-v2 [--check]

Text level only (no images). Gold validates against ml/schemas/*.v1.json; region_codes come from
data/terminology/region-tree.v1.yaml; no ICD-10 codes (LIC-002); no treatment advice, dosing or
prognosis (BR-042). Strata per record: lang (vi/en), layout (page type), noise (clean/light/heavy).
Reuses content helpers from golden-v0/v1 without changing them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import timedelta
from pathlib import Path

from . import content, pages

SEED = 20261024
PER_UNIT = 200
VERSION = "2.0.0"
LANGS = [("vi", 140), ("en", 60)]  # 70 / 30 %
NOISE = [("clean", 100), ("light", 70), ("heavy", 30)]  # 50 / 35 / 15 %
LAYOUTS = {  # page types (synth_gen.pages.TYPES) that plausibly carry each Unit's content
    "dental": ["dental_record", "outpatient_form", "discharge_summary"],
    "cardiology": ["outpatient_form", "discharge_summary", "lab_result"],
    "oncology": ["pathology_report", "discharge_summary", "outpatient_form"],
}
FILES = ("gold.jsonl", "docs.jsonl")

# (vi, en, site vi, site en, region_code)
CARDIO_DX = [
    ("Tăng huyết áp vô căn", "Essential hypertension", "Hệ tuần hoàn", "Circulatory", "sys_cardiovascular"),
    ("Bệnh mạch vành xơ vữa", "Atherosclerotic heart disease", "Động mạch vành", "Coronary artery", "coronary_arteries"),
    ("Rung nhĩ", "Atrial fibrillation", "Tâm nhĩ trái", "Left atrium", "heart_la"),
    ("Suy tim", "Heart failure", "Tim", "Heart", "heart"),
    ("Phì đại thất trái", "Left ventricular hypertrophy", "Thất trái", "Left ventricle", "heart_lv"),
    ("Hở van hai lá", "Mitral regurgitation", "Van hai lá", "Mitral valve", "valve_mitral"),
    ("Hẹp van động mạch chủ", "Aortic stenosis", "Van động mạch chủ", "Aortic valve", "valve_aortic"),
    ("Hở van ba lá", "Tricuspid regurgitation", "Van ba lá", "Tricuspid valve", "valve_tricuspid"),
    ("Tăng áp động mạch phổi", "Pulmonary hypertension", "Thân động mạch phổi", "Pulmonary trunk", "pulmonary_trunk"),
    ("Giãn động mạch chủ", "Aortic dilatation", "Động mạch chủ", "Aorta", "aorta"),
]  # fmt: skip
# (vi, en, sided, region template ({s} = l|r), histology vi, histology en)
ONCO_PRIMARY = [
    ("Vú", "Breast", True, "breast_{s}", "Ung thư biểu mô ống xâm nhập", "Invasive ductal carcinoma"),
    ("Phổi", "Lung", True, "lung_{s}", "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Đại tràng", "Colon", False, "colon", "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Tiền liệt tuyến", "Prostate", False, "prostate", "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Tuyến giáp", "Thyroid", False, "thyroid", "Ung thư biểu mô nhú", "Papillary carcinoma"),
    ("Dạ dày", "Stomach", False, "stomach", "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Tụy", "Pancreas", False, "pancreas", "Ung thư biểu mô tuyến", "Adenocarcinoma"),
    ("Bàng quang", "Bladder", False, "bladder", "Ung thư biểu mô tế bào chuyển tiếp", "Urothelial carcinoma"),
]  # fmt: skip
# Simplified, project-fixed table (not a staging reference): T, N, M, stage
TNM_STAGES = content.TNM_STAGES + [("T3", "N2", "M0", "IIIB"), ("T4", "N2", "M1", "IV")]
# (vi, en, sided, region template)
NODES = [
    ("Hạch nách", "Axillary", True, "ln_axillary_{s}"),
    ("Hạch trung thất", "Mediastinal", False, "ln_mediastinal"),
    ("Hạch rốn phổi", "Hilar", True, "ln_hilar_{s}"),
    ("Hạch cạnh động mạch chủ", "Para-aortic", False, "ln_paraaortic"),
    ("Hạch chậu", "Iliac", True, "ln_iliac_{s}"),
    ("Hạch cổ", "Cervical", True, "ln_cervical_{s}"),
]  # fmt: skip
METS = [
    ("Gan", "Liver", False, "liver"),
    ("Phổi", "Lung", True, "lung_{s}"),
    ("Não", "Brain", False, "brain"),
    ("Xương sống", "Spine bone", False, "bone_spine"),
    ("Xương chậu", "Pelvic bone", False, "bone_pelvis"),
    ("Thượng thận", "Adrenal gland", True, "adrenal_{s}"),
]  # fmt: skip
SIDE_TEXT = {"vi": {"l": "trái", "r": "phải"}, "en": {"l": "left", "r": "right"}}
SIDE_LAT = {"l": "left", "r": "right"}


def _region(code: str | None) -> dict:
    return {"region_code": code, "confidence": 1.0 if code else 0.0}


def _sided(vi: bool, name: str, sided: bool, tmpl: str, rng: random.Random):
    """-> (display text, region_code, side letter or None)."""
    s = rng.choice("lr") if sided else None
    text = name + (f" {SIDE_TEXT['vi' if vi else 'en'][s]}" if s else "")
    return text, tmpl.format(s=s), s


def build_dental(rng, lang, lines):
    lab = content.LABELS[lang]
    enc = content._encounter(rng, "dental", lang, lines)
    teeth = []
    for fdi in sorted(rng.sample(content.FDI_PERMANENT, rng.randint(2, 6))):
        cond = rng.choice(list(content.TOOTH_CONDITIONS))
        surfaces = (
            sorted(rng.sample("OMDBL", rng.randint(1, 3)))
            if cond in content.SURFACE_CONDITIONS
            else []
        )
        sev = (
            rng.choice(content.SEVERITIES)
            if cond in {"caries", "pulpitis", "periapical_lesion"}
            else None
        )
        vi, en = content.TOOTH_CONDITIONS[cond]
        text = f"{lab['tooth']} {fdi}: {vi if lang == 'vi' else en}"
        if surfaces:
            text += f" ({lab['surf']} {''.join(surfaces)})"
        if sev:
            text += f" - {content.SEVERITY_TEXT[lang][sev]}"
        lines.append(text)
        item = {
            "fdi": content._f(fdi, f"{lab['tooth']} {fdi}"),
            "condition": cond,
            "region": _region(f"tooth_{fdi}"),
        }
        if surfaces:
            item["surfaces"] = surfaces
        if sev:
            item["severity"] = sev
        teeth.append(item)
    out = {"encounter": enc, "dentition": "permanent", "teeth": teeth}
    if rng.random() < 0.3:
        q = rng.randint(1, 4)
        vi, en = rng.choice(content.PERIO)
        txt = f"{vi if lang == 'vi' else en} (Q{q})"
        lines.append(txt)
        out["periodontal"] = [
            {"quadrant": q, "condition": content._f(vi if lang == "vi" else en, txt)}
        ]
    return out


def build_cardiology(rng, lang, lines):
    lab = content.LABELS[lang]
    vi = lang == "vi"
    enc = content._encounter(rng, "cardiology", lang, lines)
    diagnoses = []
    lines.append(f"{lab['dx']}:")
    for dvi, den, svi, sen, region in rng.sample(CARDIO_DX, rng.randint(1, 3)):
        name, site = (dvi, svi) if vi else (den, sen)
        sev = rng.choice([None, *content.SEVERITIES])
        lines.append(f"- {name}" + (f" - {content.SEVERITY_TEXT[lang][sev]}" if sev else ""))
        diagnoses.append(
            {
                "text": content._f(name, name),
                "site": content._f(site, site),
                "laterality": "unknown",
                "severity": sev,
                "region": _region(region),
            }
        )
    observations = []
    lines.append(f"{lab['obs']}:")
    for nvi, nen, loinc, unit, lo, hi, ref in rng.sample(content.CARDIO_OBS, rng.randint(3, 6)):
        name = nvi if vi else nen
        val = round(rng.uniform(lo, hi), 2 if hi < 1 else (1 if hi < 100 else 0))
        lines.append(f"{name}: {val:g} {unit}  ({lab['ref']} {ref})")
        observations.append(
            {
                "name": content._f(name, name),
                "value": {**content._f(val, f"{val:g} {unit}"), "unit": unit},
                "reference_range": content._f(ref, ref),
                "loinc_hint": loinc,
            }
        )
    out = {"encounter": enc, "diagnoses": diagnoses, "observations": observations}
    procs = rng.sample(content.CARDIO_PROCS, rng.randint(0, 3))
    if procs:
        lines.append(f"{lab['proc']}:")
        out["procedures"] = []
        for pvi, pen in procs:
            p = pvi if vi else pen
            lines.append(f"- {p}")
            out["procedures"].append(content._f(p, p))
    return out


def build_oncology(rng, lang, lines):
    lab = content.LABELS[lang]
    vi = lang == "vi"
    enc = content._encounter(rng, "oncology", lang, lines)
    pvi, pen, sided, tmpl, hvi, hen = rng.choice(ONCO_PRIMARY)
    site, pregion, side = _sided(vi, pvi if vi else pen, sided, tmpl, rng)
    hist = hvi if vi else hen
    size, grade = rng.randint(8, 60), f"G{rng.randint(1, 3)}"
    t, n, m, stage = rng.choice(TNM_STAGES)
    lines.append(f"{lab['primary']}: {site}")
    lines.append(f"{lab['histology']}: {hist}")
    lines.append(f"{lab['size']}: {size} mm; {lab['grade']}: {grade}")
    lines.append(f"{lab['tnm']}: {t} {n} {m} (AJCC 8); {lab['stage']}: {stage}")
    out = {
        "encounter": enc,
        "primary": {
            "site": content._f(site, site),
            "laterality": SIDE_LAT[side] if side else "midline",
            "histology": content._f(hist, hist),
            "size_mm": {**content._f(size, f"{size} mm"), "unit": "mm"},
            "grade": content._f(grade, grade),
            "region": _region(pregion),
        },
        "tnm": {
            "t": content._f(t, t),
            "n": content._f(n, n),
            "m": content._f(m, m),
            "stage": content._f(stage, stage),
            "edition": "AJCC 8",
        },
        "nodes": [],
        "metastases": [],
        "treatments": [],
    }
    # N1 -> 1 involved station, N2 -> 2; N0 sometimes lists a station as NOT involved (negation).
    k = {"N0": rng.choice([0, 0, 1]), "N1": 1, "N2": 2}[n]
    for nvi, nen, nsided, ntmpl in rng.sample(NODES, k):
        st, nregion, _ = _sided(vi, nvi if vi else nen, nsided, ntmpl, rng)
        involved = n != "N0"
        lines.append(
            f"{lab['node']}: {st} - {lab['involved'] if involved else lab['not_involved']}"
        )
        out["nodes"].append(
            {"station": content._f(st, st), "involved": involved, "region": _region(nregion)}
        )
    if m == "M1":
        for mvi, men, msided, mtmpl in rng.sample(METS, rng.randint(1, 3)):
            ms, mregion, _ = _sided(vi, mvi if vi else men, msided, mtmpl, rng)
            stated = rng.choice(["confirmed", "suspected"])
            lines.append(f"{lab['mets']}: {ms} ({lab[stated]})")
            out["metastases"].append(
                {"site": content._f(ms, ms), "stated_as": stated, "region": _region(mregion)}
            )
    for _ in range(rng.choice([0, 0, 1, 2])):
        ttype, tvi, ten = rng.choice(content.TREATMENT_HISTORY)
        tdate = (content._date(rng) - timedelta(days=rng.randint(60, 300))).isoformat()
        lines.append(f"{lab['history']}: {tvi if vi else ten} {tdate}")
        out["treatments"].append({"type": ttype, "date": content._f(tdate, tdate)})
    return out


BUILDERS = {"dental": build_dental, "cardiology": build_cardiology, "oncology": build_oncology}

# Deterministic OCR-like damage on the rendered text (gold is unaffected).
_CONFUSE = {"l": "1", "O": "0", "0": "O", "1": "l", "S": "5", "B": "8", "m": "rn", "e": "c"}
_ACCENTS = str.maketrans(
    "ăâêôơưđáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ", "aaeooudaaaaaeeeeeiiiiiooooouuuuuyyyyy"
)


def add_noise(text: str, level: str, rng: random.Random) -> str:
    if level == "clean":
        return text
    p_sub, p_acc = (0.02, 0.05) if level == "light" else (0.08, 0.3)
    out = []
    for ch in text:
        if ch.lower() in "ăâêôơưđáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ" and rng.random() < p_acc:
            ch = ch.translate(_ACCENTS) if ch.islower() else ch.lower().translate(_ACCENTS).upper()
        elif ch in _CONFUSE and rng.random() < p_sub:
            ch = _CONFUSE[ch]
        out.append(ch)
    return "".join(out)


def plan(seed: int = SEED) -> list[dict]:
    """Per-record unit/lang/noise/layout; each stratum shuffled independently per Unit."""
    specs = []
    for unit in content.BUILDERS:
        rng = random.Random(f"{seed}:plan:{unit}")  # noqa: S311 - deterministic synthetic data
        langs = [x for x, n in LANGS for _ in range(round(PER_UNIT * n / 200))]
        noises = [x for x, n in NOISE for _ in range(n)]
        layouts = [LAYOUTS[unit][i % 3] for i in range(PER_UNIT)]
        for lst in (langs, noises, layouts):
            rng.shuffle(lst)
        specs += [
            {"unit": unit, "lang": a, "noise": b, "layout": c}
            for a, b, c in zip(langs, noises, layouts, strict=True)
        ]
    return specs


def generate_record(index: int, spec: dict, seed: int = SEED) -> tuple[dict, dict]:
    rng = random.Random(f"{seed}:{index}")  # noqa: S311 - deterministic synthetic data
    unit, lang = spec["unit"], spec["lang"]
    lab = content.LABELS[lang]
    patient = content.make_patient(rng)
    titles = pages.TITLES[spec["layout"]]
    title = rng.choice(titles[:2] if lang == "vi" else titles[2:4])
    header = [
        f"{title} ({pages.FOOTER})",
        f"{lab['patient']}: {patient['name']}",
        f"{lab['birth']}: {patient['birth_year']}    {lab['sex']}: "
        f"{lab['female'] if patient['sex'] == 'female' else lab['male']}",
    ]
    lines: list[str] = []
    fields = BUILDERS[unit](rng, lang, lines)
    doc_id = f"gv2-{index + 1:03d}-{unit}-{lang}"
    strata = {"lang": lang, "layout": spec["layout"], "noise": spec["noise"]}
    text = "\n".join([*header, *lines])
    nrng = random.Random(f"{seed}:{index}:noise")  # noqa: S311 - deterministic synthetic data
    gold = {
        "doc_id": doc_id,
        "unit": unit,
        "quality": spec["noise"],
        "strata": strata,
        "fields": fields,
    }
    doc = {
        "doc_id": doc_id,
        "unit": unit,
        "strata": strata,
        "patient": patient,
        "text_clean": text,
        "text": add_noise(text, spec["noise"], nrng),
        "generator_version": VERSION,
        "seed": seed,
    }
    return gold, doc


def _dump(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)


def build(seed: int = SEED) -> dict[str, str]:
    pairs = [generate_record(i, s, seed) for i, s in enumerate(plan(seed))]
    files = {"gold.jsonl": _dump([g for g, _ in pairs]), "docs.jsonl": _dump([d for _, d in pairs])}
    sums = {k: hashlib.sha256(v.encode("utf-8")).hexdigest() for k, v in files.items()}
    counts = {}
    for g, _ in pairs:
        for key in (g["unit"], *(f"{k}={v}" for k, v in g["strata"].items())):
            counts[key] = counts.get(key, 0) + 1
    manifest = {
        "name": "golden-v2",
        "version": VERSION,
        "seed": seed,
        "docs": len(pairs),
        "sha256": sums,
        "counts": dict(sorted(counts.items())),
    }
    files["manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--check", action="store_true", help="exit 1 if --out differs from a rebuild")
    a = ap.parse_args()
    files = build(a.seed)
    if a.check:
        bad = [k for k, v in files.items() if (a.out / k).read_text(encoding="utf-8") != v]
        print("golden-v2 " + ("DIFFERS: " + ", ".join(bad) if bad else "up to date"))
        return 1 if bad else 0
    a.out.mkdir(parents=True, exist_ok=True)
    for k, v in files.items():
        (a.out / k).write_text(v, encoding="utf-8")
    print(f"wrote {len(files)} files to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
