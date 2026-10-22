"""Rule-based PII redaction (VI + EN), ported from the ai-ml-engineer pii_redact.py script.

First layer only (SEC-AI-02): callers must treat any exception as fail-closed (O-03).
The placeholder->original map is deliberately not kept or returned.
"""

import re

_NAME = r"[A-ZÀ-Ỹ][\wÀ-ỹ'’-]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ'’-]*){0,4}"

# (label, pattern, group-only). Order matters: more specific first.
_PATTERNS: list[tuple[str, re.Pattern[str], bool]] = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), False),
    ("NATIONAL_ID", re.compile(r"(?<!\d)\d{12}(?!\d)"), False),
    ("OLD_ID", re.compile(r"(?<!\d)\d{9}(?!\d)"), False),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){9,10}(?!\d)"), False),
    ("INSURANCE_ID", re.compile(r"\b[A-Z]{2}\d{13}\b"), False),
    (
        "PATIENT_CODE",
        re.compile(
            r"(?i)\b(?:mã\s*(?:bn|bệnh nhân|y tế|hồ sơ)|mrn|patient\s*id|record\s*(?:no|number|#))"
            r"[:\s#.]*([A-Z0-9][A-Z0-9-]{3,})"
        ),
        True,
    ),
    (
        "LABELLED_NAME",
        re.compile(
            r"(?i)(?:họ\s*(?:và)?\s*tên|tên\s*bệnh\s*nhân|patient\s*name|name)\s*[:\-]\s*([^\n,;]{2,60})"
        ),
        True,
    ),
    (
        "HONORIFIC_NAME",
        re.compile(
            r"\b(?:Ông|Bà|Anh|Chị|Cô|Chú|Bác sĩ|BS\.?|Mr\.?|Mrs\.?|Ms\.?|Miss|Dr\.?)\s+("
            + _NAME
            + ")"
        ),
        True,
    ),
    (
        "LABELLED_ADDRESS",
        re.compile(r"(?i)(?:địa\s*chỉ|address)\s*[:\-]\s*([^\n]{4,120})"),
        True,
    ),
    (
        "ADDRESS_HINT",
        re.compile(
            r"(?i)\b(?:số\s*\d+[\w/]*\s+)?(?:đường|phố|phường|quận|huyện|xã|thôn|"
            r"ward|district|street)\s+[\wÀ-ỹ]+(?:[\s,]+[\wÀ-ỹ]+){0,3}"
        ),
        False,
    ),
    (
        "DOB",
        re.compile(
            r"(?i)(?:ngày\s*sinh|dob|date\s*of\s*birth)\s*[:\-]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})"
        ),
        True,
    ),
]


def redact(text: str) -> str:
    """Return text with PII replaced by stable placeholders like [PHONE_1]."""
    if not isinstance(text, str):
        raise TypeError("redact() expects str")
    counters: dict[str, int] = {}

    def factory(label: str, group_only: bool):
        def repl(m: re.Match[str]) -> str:
            counters[label] = counters.get(label, 0) + 1
            ph = f"[{label}_{counters[label]}]"
            if group_only and m.lastindex:
                s, e = m.span(1)
                base = m.start()
                return m.group(0)[: s - base] + ph + m.group(0)[e - base :]
            return ph

        return repl

    for label, pat, group_only in _PATTERNS:
        text = pat.sub(factory(label, group_only), text)
    return text
