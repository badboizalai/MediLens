#!/usr/bin/env python3
"""Find risky medical/marketing claims in MediLens text (Vietnamese + English).

Usage:
  python claims_lint.py <file-or-folder> [...] [--allowlist allow.txt] [--json]

Scans .md .txt .html .json .tsx .ts .jsx .js .yaml .yml files. Matching is
case- and accent-insensitive (Vietnamese diacritics and đ are folded), so
"chan doan" and "chẩn đoán" are both found. A line containing "claims-ok"
is skipped (use it for legitimate quotes of a record field, e.g.
"Chẩn đoán (theo hồ sơ)" // claims-ok). An allowlist file holds exact
lines/phrases (one per line) to skip.
Exit code 1 if any BLOCK finding remains.
"""
import json
import os
import re
import sys
import unicodedata

EXTS = {".md", ".txt", ".html", ".json", ".tsx", ".ts", ".jsx", ".js", ".yaml", ".yml"}

# (level, pattern on folded text, suggestion)
RULES = [
    ("BLOCK", r"\b(giup|tu|ai|tro ly|ung dung|app)\s+chan doan\b", "Use 'giúp bạn hiểu thông tin trong hồ sơ'"),
    ("BLOCK", r"\bphat hien (som |)(benh|ung thu|khoi u|ton thuong)\b", "Use 'hiển thị các phát hiện đã ghi trong hồ sơ'"),
    ("BLOCK", r"\bthay the (cho )?bac si\b", "Use 'dùng cùng với lời khuyên của bác sĩ'"),
    ("BLOCK", r"\bkhong can (di )?kham\b", "Remove; always advise seeing a clinician"),
    ("BLOCK", r"\b(goi y|de xuat|khuyen nghi) (phac do |)dieu tri\b", "Remove treatment advice"),
    ("BLOCK", r"\blieu (dung|luong)\b", "Remove dosing content"),
    ("BLOCK", r"\bnen (uong|dung|ngung) thuoc\b", "Remove medication advice"),
    ("BLOCK", r"\btien luong\b", "Remove prognosis"),
    ("BLOCK", r"\b(du doan|uoc tinh) (thoi gian )?song\b", "Remove survival prediction"),
    ("BLOCK", r"\bchinh xac 100\s?%", "State measured accuracy with scope, or nothing"),
    ("BLOCK", r"\b(duoc )?bo y te (cap phep|chung nhan|phe duyet)\b", "Only if true and documented"),
    ("BLOCK", r"\b(ai |helps? (you )?|can |will )?diagnos(e|es|ing)\b", "Use 'helps you understand your records'"),
    ("BLOCK", r"\b(ai|automated) diagnosis\b", "Use 'shows findings written in your records'"),
    ("BLOCK", r"\bdetects? (early )?(disease|cancer|tumou?rs?|lesions?)\b", "Use 'shows findings written in your records'"),
    ("BLOCK", r"\bearly detection\b", "Remove detection claim"),
    ("BLOCK", r"\breplaces? (your |a )?(doctor|physician|clinician)\b", "Use 'use alongside your doctor's advice'"),
    ("BLOCK", r"\bno need to see a doctor\b", "Remove"),
    ("BLOCK", r"\btreatment recommendations?\b", "Remove treatment advice"),
    ("BLOCK", r"\b(dosage|dosing)\b", "Remove dosing content"),
    ("BLOCK", r"\bprognos(is|es|tic)\b", "Remove prognosis"),
    ("BLOCK", r"\bsurvival (rate|time|prediction)s?\b", "Remove survival content"),
    ("BLOCK", r"\b100\s?% accurate\b", "State measured accuracy with scope, or nothing"),
    ("BLOCK", r"\b(fda|ce|ministry of health)[- ](approved|cleared|certified)\b", "Only if true and documented"),
    ("REVIEW", r"\bchan doan\b", "OK only when quoting the record field (mark claims-ok)"),
    ("REVIEW", r"\bdiagnosis\b", "OK only when quoting the record field (mark claims-ok)"),
    ("REVIEW", r"\b(an toan|bao mat) tuyet doi\b", "Use 'được mã hóa và kiểm soát truy cập'"),
    ("REVIEW", r"\b(completely|100\s?%) secure\b", "Use 'encrypted and access-controlled'"),
    ("REVIEW", r"\b(clinically (validated|proven)|duoc bac si kiem chung)\b", "Only with a VAL report and its scope"),
]
COMPILED = [(lvl, re.compile(p), sug) for lvl, p, sug in RULES]


def fold(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def iter_files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                if any(part in root for part in ("node_modules", ".git", "dist")):
                    continue
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in EXTS:
                        yield os.path.join(root, f)
        elif os.path.isfile(p):
            yield p


def scan(path, allow):
    findings = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            if "claims-ok" in line or line.strip() in allow:
                continue
            folded = fold(line)
            hit_spans = []
            for lvl, rx, sug in COMPILED:
                for m in rx.finditer(folded):
                    span = (m.start(), m.end())
                    # a REVIEW rule is skipped when a BLOCK rule already covers the span
                    if lvl == "REVIEW" and any(s <= span[0] and span[1] <= e for s, e, _l in hit_spans):
                        continue
                    hit_spans.append((span[0], span[1], lvl))
                    findings.append({"file": path, "line": lineno, "level": lvl,
                                     "match": m.group(0), "suggestion": sug,
                                     "text": line.strip()[:160]})
    return findings


def main(argv):
    args = [a for a in argv[1:]]
    if not args:
        print(__doc__)
        return 2
    as_json = "--json" in args
    allow = set()
    if "--allowlist" in args:
        i = args.index("--allowlist")
        with open(args[i + 1], encoding="utf-8") as fh:
            allow = {ln.strip() for ln in fh if ln.strip()}
        del args[i:i + 2]
    paths = [a for a in args if not a.startswith("--")]
    findings = []
    for f in iter_files(paths):
        findings.extend(scan(f, allow))
    blocks = sum(1 for f in findings if f["level"] == "BLOCK")
    reviews = sum(1 for f in findings if f["level"] == "REVIEW")
    if as_json:
        print(json.dumps({"block": blocks, "review": reviews, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{f['level']:6} {f['file']}:{f['line']}  '{f['match']}'  → {f['suggestion']}\n        {f['text']}")
        print(f"BLOCK={blocks} REVIEW={reviews} → {'FAIL' if blocks else 'PASS'}")
    return 1 if blocks else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
