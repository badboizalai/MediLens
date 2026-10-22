#!/usr/bin/env python3
"""Run simple data quality rules on a CSV or JSONL file.

Usage:
    python dq_check.py data.csv rules.json
    python dq_check.py --example-rules > rules.json

Rule types: not_null, unique, accepted_values, regex, range, fdi, pii_scan.
Each rule: {"id": "DQ-04", "column": "fdi", "type": "fdi", "severity": "MUST"}.
Exit code 1 if any MUST rule fails.
"""
import csv
import json
import re
import sys

FDI = {f"{q}{p}" for q in range(1, 5) for p in range(1, 9)} | {f"{q}{p}" for q in range(5, 9) for p in range(1, 6)}
PII = [re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), re.compile(r"(?<!\d)(?:\+?84|0)\d{9,10}(?!\d)"), re.compile(r"(?<!\d)\d{12}(?!\d)")]

EXAMPLE = [
    {"id": "DQ-01", "column": "icd10_code", "type": "not_null", "severity": "MUST"},
    {"id": "DQ-04", "column": "fdi", "type": "fdi", "severity": "MUST"},
    {"id": "DQ-05", "column": "value", "type": "range", "min": 0, "max": 1000, "severity": "SHOULD"},
    {"id": "DQ-08", "column": "sha256", "type": "unique", "severity": "MUST"},
    {"id": "DQ-X1", "column": "status", "type": "accepted_values", "values": ["draft", "confirmed"], "severity": "MUST"},
    {"id": "DQ-13", "column": "*", "type": "pii_scan", "severity": "MUST"},
]


def load(path):
    if path.endswith(".jsonl"):
        return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def check(rule, rows):
    col, t = rule.get("column"), rule["type"]
    bad = []
    if t == "unique":
        seen = {}
        for i, r in enumerate(rows):
            v = r.get(col)
            if v in seen:
                bad.append(i)
            seen[v] = i
        return bad
    for i, r in enumerate(rows):
        v = r.get(col) if col != "*" else None
        if t == "not_null" and v in (None, ""):
            bad.append(i)
        elif t == "accepted_values" and v not in rule["values"]:
            bad.append(i)
        elif t == "regex" and v not in (None, "") and not re.fullmatch(rule["pattern"], str(v)):
            bad.append(i)
        elif t == "range" and v not in (None, ""):
            try:
                f = float(v)
                if f < rule.get("min", float("-inf")) or f > rule.get("max", float("inf")):
                    bad.append(i)
            except ValueError:
                bad.append(i)
        elif t == "fdi" and v not in (None, "") and str(v) not in FDI:
            bad.append(i)
        elif t == "pii_scan":
            text = " ".join(str(x) for x in r.values())
            if any(p.search(text) for p in PII):
                bad.append(i)
    return bad


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--example-rules":
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    rows, rules = load(sys.argv[1]), json.load(open(sys.argv[2], encoding="utf-8"))
    must_fail = False
    print(f"rows: {len(rows)}")
    for rule in rules:
        bad = check(rule, rows)
        status = "PASS" if not bad else "FAIL"
        if bad and rule.get("severity", "MUST") == "MUST":
            must_fail = True
        sample = ", ".join(str(i + 1) for i in bad[:5])
        print(f"{status:4} {rule['id']:<7} {rule['type']:<15} {rule.get('column', ''):<14} failures={len(bad)} {('rows: ' + sample) if bad else ''}")
    return 1 if must_fail else 0


if __name__ == "__main__":
    sys.exit(main())
