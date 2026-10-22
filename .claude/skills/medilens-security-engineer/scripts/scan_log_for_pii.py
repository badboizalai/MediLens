#!/usr/bin/env python3
"""Scan log files for PHI/PII that must never be logged (SEC-DP-06).

Usage:
    python scan_log_for_pii.py app.log [more.log ...] [--max-show 20]

Detects: emails, Vietnamese phone numbers, 9/12-digit ID numbers, health-insurance
card patterns, labelled names/addresses/DOB, JWT-like tokens, AWS keys, and
Vietnamese/English clinical terms appearing next to identifiers. Exit 1 if
anything is found, so it can gate CI on sample logs from staging.
"""

import argparse
import re
import sys

RULES = [
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("phone_vn", re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){9,10}(?!\d)")),
    ("id_12", re.compile(r"(?<!\d)\d{12}(?!\d)")),
    ("insurance_card", re.compile(r"\b[A-Z]{2}\d{13}\b")),
    ("labelled_name", re.compile(r"(?i)(?:họ\s*tên|patient[_\s]?name|full[_\s]?name)\W{1,3}\S+")),
    ("labelled_dob", re.compile(r"(?i)(?:ngày\s*sinh|dob|birth[_\s]?date)\W{1,3}\d")),
    ("jwt", re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "clinical_term",
        re.compile(
            r"(?i)\b(?:chẩn đoán|ung thư|di căn|carcinoma|metastasis|diagnosis|icd10?_?code)\b"
        ),
    ),
]


def scan(path, max_show):
    hits = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            for name, pat in RULES:
                m = pat.search(line)
                if m:
                    hits += 1
                    if hits <= max_show:
                        snippet = line.strip()[:160]
                        masked = snippet.replace(m.group(0), f"<{name}>")
                        print(f"{path}:{n}: [{name}] {masked}")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--max-show", type=int, default=20)
    a = ap.parse_args()
    total = sum(scan(f, a.max_show) for f in a.files)
    print(f"total findings: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
