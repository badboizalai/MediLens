#!/usr/bin/env python3
"""Rule-based PII redaction for Vietnamese/English medical text (first layer).

Usage:
    python pii_redact.py "Họ tên: Nguyễn Văn A, SĐT 0912 345 678, CCCD 012345678901"
    python pii_redact.py --file ocr.txt [--map map.json]
    python pii_redact.py --test

Replaces matches with stable placeholders like [PHONE_1] and can write the
placeholder→original map (keep it inside the PHI boundary; never send it out).
This is a first layer only: combine with an NER model for names/addresses
written without labels, and measure recall on a labelled set (target ≥ 99%).
"""

import argparse
import json
import re

PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("NATIONAL_ID", re.compile(r"(?<!\d)\d{12}(?!\d)")),  # CCCD 12 digits
    ("OLD_ID", re.compile(r"(?<!\d)\d{9}(?!\d)")),  # CMND 9 digits
    ("PHONE", re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){9,10}(?!\d)")),
    ("INSURANCE_ID", re.compile(r"\b[A-Z]{2}\d{13}\b")),  # BHYT card pattern
    (
        "PATIENT_CODE",
        re.compile(r"(?i)\b(?:mã\s*(?:bn|bệnh nhân|y tế)|mrn|patient\s*id)[:\s#]*([A-Z0-9-]{4,})"),
    ),
    (
        "LABELLED_NAME",
        re.compile(
            r"(?i)(?:họ\s*(?:và)?\s*tên|tên\s*bệnh\s*nhân|patient\s*name|name)\s*[:\-]\s*([^\n,;]{2,60})"
        ),
    ),
    ("LABELLED_ADDRESS", re.compile(r"(?i)(?:địa\s*chỉ|address)\s*[:\-]\s*([^\n]{4,120})")),
    (
        "DOB",
        re.compile(
            r"(?i)(?:ngày\s*sinh|dob|date\s*of\s*birth)\s*[:\-]?\s*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})"
        ),
    ),
]


def redact(text: str):
    mapping, counters = {}, {}

    def repl_factory(label, group_only):
        def repl(m):
            target = m.group(1) if group_only and m.lastindex else m.group(0)
            counters[label] = counters.get(label, 0) + 1
            ph = f"[{label}_{counters[label]}]"
            mapping[ph] = target
            return m.group(0).replace(target, ph) if group_only and m.lastindex else ph

        return repl

    for label, pat in PATTERNS:
        group_only = label in {"PATIENT_CODE", "LABELLED_NAME", "LABELLED_ADDRESS", "DOB"}
        text = pat.sub(repl_factory(label, group_only), text)
    return text, mapping


def _test():
    t = "Họ tên: Nguyễn Văn An, SĐT 0912 345 678, CCCD 012345678901, email a@b.vn. CĐ: THA, răng 36."
    out, m = redact(t)
    for secret in ("Nguyễn Văn An", "0912 345 678", "012345678901", "a@b.vn"):
        assert secret not in out, (secret, out)
    assert "răng 36" in out and "THA" in out
    print(out)
    print("all tests passed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--map")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        return _test()
    text = open(a.file, encoding="utf-8").read() if a.file else " ".join(a.text)
    out, mapping = redact(text)
    print(out)
    if a.map:
        json.dump(mapping, open(a.map, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
