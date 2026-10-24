"""Deterministic safety guardrails for explanation/Q&A traffic (BR-023, BR-041, BR-042).

Input check runs before any provider call; output check runs on the provider answer.
Rules are regex on diacritic-stripped lowercase text, so VI with or without diacritics
and EN share one rule set. Nothing here logs or stores prompt text.
shortcut: regex rules, no classifier; upgrade with the S10-T98 red-team misses.
"""

import re
import unicodedata
from dataclasses import dataclass

# Precedence: emergency first (115 beats refusal), then the refusal categories.
_INPUT_RULES: dict[str, str] = {
    "emergency": (
        r"dau nguc|kho tho|khong tho duoc|ngat xiu|bat tinh|co giat|dot quy|meo mieng|"
        r"yeu (nua nguoi|liet)|chay mau (nhieu|khong cam)|(non|ho) ra mau|"
        r"uong qua lieu|chest (pain|tightness)|short(ness)? of breath|"
        r"(can ?not|can't|cant|trouble|difficulty) breath|heart attack|"
        r"severe bleeding|unconscious|seizure|overdos|suicid|having a stroke"
    ),
    "dosing": (
        r"bao nhieu (mg|ml|mcg|vien|lieu|goi|giot)|uong (bao nhieu|may) vien|lieu (luong|dung)|"
        r"(ngay|mot ngay) (may|bao nhieu) lan|may lan (mot |1 )?ngay|"
        r"how many (mg|ml|mcg|milligrams|pills|tablets|capsules|drops|units)|"
        r"\b(what|which) (dose|dosage)|\bdosage\b|how much .{0,30}\b(take|medicine|medication|drug)|"
        r"how (often|many times) .{0,20}\btake"
    ),
    "med_change": (
        r"(ngung|bo|doi|giam|tang|quen) (uong )?(thuoc|lieu)|nen (ngung|bo|doi|dung|uong) .{0,20}thuoc|"
        r"(stop|quit|skip|halt|change|switch|increase|reduce|double) ([\w']+ ){0,3}"
        r"(medic|meds|pill|tablet|dose|drug|prescription|insulin|statin|blood thinner|anticoag)"
    ),
    "prognosis": (
        r"song (duoc |them )?(bao lau|may nam|may thang)|con (bao lau|song)|tien luong|ty le song|"
        r"song sot|(co|se|sap) chet|bao lau nua .{0,15}(chet|mat)|"
        r"how long (do i|will i|can i|does he|does she) (have|live|survive)|life expectancy|"
        r"survival (rate|time)|prognosis|will i die|am i dying|terminally|terminal (illness|cancer|stage)"
    ),
    "diagnosis": (
        r"toi (bi|mac) (benh )?(gi|sao)|chan doan (cho )?(toi|giup)|"
        r"co phai (toi |la |no |minh )*(bi |mac )?(ung thu|tieu duong|benh)|"
        r"toi co (bi|mac) .{0,30}khong|toi co phai (la )?(bi|mac|benh)|"
        r"what (disease|illness|condition)|what('s| is) wrong|do i have (?!to\b)|am i (sick|ill)|"
        r"diagnose (me|my)|is (it|this) (cancer|serious|a tumou?r)"
    ),
}

_OUTPUT_RULES: dict[str, str] = {
    # mg/dL etc. are lab units, so a bare mg followed by "/" is allowed.
    "dosing": (
        r"\b\d+(?:[.,]\d+)?\s*(?:mg(?!/)|mcg|ml\b|vien\b|lan\s*/\s*ngay|lan mot ngay|"
        r"tablets?\b|pills?\b|capsules?\b|times (?:a|per) day)"
    ),
    "prognosis": (
        r"\bsong (?:duoc )?(?:them )?\d+ (?:thang|nam|tuan)|\bcon (?:khoang )?\d+ (?:thang|nam|tuan)|"
        r"\d+ (?:months?|years?|weeks?) to live|median survival|"
        r"\b(?:5|five)[- ]year survival (?:rate )?(?:is|of)"
    ),
    "diagnosis": (
        r"\b(?:you|ban) (?:have|has|bi|mac|likely have|probably have)\s+"
        r"(?:cancer|a tumou?r|diabetes|ung thu|tieu duong|u ac)"
    ),
}

_COMPILED_IN = {k: re.compile(v) for k, v in _INPUT_RULES.items()}
_COMPILED_OUT = {k: re.compile(v) for k, v in _OUTPUT_RULES.items()}

_COPY = {
    "emergency": {
        "vi": (
            "Hãy gọi 115 ngay hoặc đến cơ sở cấp cứu gần nhất để được chăm sóc tức thì. "
            "Đây có thể là dấu hiệu cần nhân viên y tế đánh giá khẩn cấp; "
            "bạn đừng chờ thêm và nên nhờ người ở gần ở bên cạnh."
        ),
        "en": (
            "Call 115 now or go to the nearest emergency department for immediate care. "
            "These can be signs that need urgent assessment by medical staff; "
            "please do not wait, and ask someone nearby to stay with you."
        ),
    },
    "refusal": {
        "vi": (
            "MediLens chỉ giúp giải thích hồ sơ và thuật ngữ y khoa, không đưa ra liều dùng, "
            "thay đổi thuốc, chẩn đoán hay tiên lượng. Bác sĩ điều trị biết rõ tình trạng của bạn "
            "nhất, hãy hỏi trực tiếp bác sĩ hoặc dược sĩ của bạn. Mình rất sẵn lòng giải thích "
            "các thuật ngữ trong hồ sơ."
        ),
        "en": (
            "MediLens only helps explain records and medical terms; it does not give doses, "
            "medication changes, diagnoses or prognosis. Your treating clinician knows your "
            "situation best, so please ask your doctor or pharmacist directly. I am happy to "
            "explain any terms in your record."
        ),
    },
}


@dataclass(frozen=True)
class GuardrailResult:
    category: str
    action: str  # "emergency" | "blocked_input" | "blocked_output"
    text: str


def normalise(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    return "".join(c for c in s if not unicodedata.combining(c))


def _reply(category: str, action: str, locale: str) -> GuardrailResult:
    key = "emergency" if category == "emergency" else "refusal"
    lang = "en" if locale.lower().startswith("en") else "vi"
    return GuardrailResult(category, action, _COPY[key][lang])


def classify_input(text: str) -> str | None:
    n = normalise(text)
    return next((c for c, rx in _COMPILED_IN.items() if rx.search(n)), None)


def check_input(text: str, locale: str = "vi") -> GuardrailResult | None:
    cat = classify_input(text)
    if cat is None:
        return None
    return _reply(cat, "emergency" if cat == "emergency" else "blocked_input", locale)


def check_output(text: str, locale: str = "vi") -> GuardrailResult | None:
    n = normalise(text)
    for cat, rx in _COMPILED_OUT.items():
        if rx.search(n):
            return _reply(cat, "blocked_output", locale)
    return None
