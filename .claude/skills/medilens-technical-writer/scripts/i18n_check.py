#!/usr/bin/env python3
"""Compare MediLens message files (nested JSON) between two locales.

Usage: python i18n_check.py messages/vi.json messages/en.json [--allow-same key1,key2]

Reports keys missing in either file, empty values, ICU placeholder mismatches
({name}, {count, plural, ...}), values identical in both files (likely
untranslated, except short codes/brand names or --allow-same keys), and risky
claim words (diagnose/detect disease/replace doctor/prognosis; chẩn đoán in
non-quote context). Exit 1 on missing keys, empty values or placeholder errors.
"""
import json
import re
import sys
import unicodedata

PH_RX = re.compile(r"\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:,|\})")
CLAIM_RX = [re.compile(p) for p in (
    r"\bdiagnos(e|es|is|ing)\b", r"\bdetects? (disease|cancer|tumou?rs?)\b", r"\breplaces? (your )?doctor\b",
    r"\bprognos(is|tic)\b", r"\b(giup|tu|ai) chan doan\b", r"\bphat hien (benh|ung thu)\b", r"\bthay the bac si\b",
    r"\btien luong\b")]
SAME_OK = re.compile(r"^[A-Z0-9 ._%/+-]{1,12}$|^MediLens|^https?://|^\{[^}]+\}$")


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def fold(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def main(argv):
    args = argv[1:]
    if len(args) < 2:
        print(__doc__)
        return 2
    allow_same = set()
    if "--allow-same" in args:
        allow_same = set(args[args.index("--allow-same") + 1].split(","))
    a_path, b_path = args[0], args[1]
    a = flatten(json.load(open(a_path, encoding="utf-8")))
    b = flatten(json.load(open(b_path, encoding="utf-8")))
    errors, warns = [], []
    for k in sorted(set(a) - set(b)):
        errors.append(f"missing in {b_path}: {k}")
    for k in sorted(set(b) - set(a)):
        errors.append(f"missing in {a_path}: {k}")
    for k in sorted(set(a) & set(b)):
        va, vb = str(a[k]), str(b[k])
        if not va.strip() or not vb.strip():
            errors.append(f"empty value: {k}")
            continue
        pa, pb = set(PH_RX.findall(va)), set(PH_RX.findall(vb))
        if pa != pb:
            errors.append(f"placeholder mismatch {k}: {sorted(pa)} vs {sorted(pb)}")
        if va == vb and k not in allow_same and not SAME_OK.match(va):
            warns.append(f"identical in both locales (untranslated?): {k} = {va[:40]!r}")
        for text, path in ((va, a_path), (vb, b_path)):
            if "claims-ok" in text:
                continue
            f = fold(text)
            for rx in CLAIM_RX:
                if rx.search(f):
                    warns.append(f"risky claim in {path} {k}: {text[:60]!r} (run claims_lint / Regulatory review)")
                    break
    print(f"{a_path}: {len(a)} keys · {b_path}: {len(b)} keys")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("RESULT:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
