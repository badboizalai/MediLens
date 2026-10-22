#!/usr/bin/env python3
"""Pseudonymise identifier columns with HMAC-SHA256 and drop PII columns.

Usage:
    MEDILENS_HMAC_KEY=... python pseudonymize.py in.csv out.csv --hash user_id profile_id --drop email phone full_name
    MEDILENS_HMAC_KEY=... python pseudonymize.py in.jsonl out.jsonl --hash user_id --drop email --birth-year-band birth_year

- The key comes from the environment (in AWS: injected from Secrets Manager); never hard-code it.
- Same input + same key → same pseudonym, so joins across tables still work.
- --birth-year-band turns a year into a 5-year band (e.g. 1987 → "1985-1989").
"""

import argparse
import csv
import hashlib
import hmac
import json
import os
import sys


def pseudo(key: bytes, value) -> str | None:
    if value in (None, ""):
        return None
    return hmac.new(key, str(value).encode("utf-8"), hashlib.sha256).hexdigest()


def band(value):
    try:
        y = int(value)
    except (TypeError, ValueError):
        return None
    lo = y - y % 5
    return f"{lo}-{lo + 4}"


def transform(rec: dict, key: bytes, hash_cols, drop_cols, band_cols) -> dict:
    out = {k: v for k, v in rec.items() if k not in drop_cols}
    for c in hash_cols:
        if c in out:
            out[c] = pseudo(key, out[c])
    for c in band_cols:
        if c in out:
            out[c] = band(out[c])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--hash", nargs="*", default=[])
    ap.add_argument("--drop", nargs="*", default=[])
    ap.add_argument("--birth-year-band", nargs="*", default=[])
    a = ap.parse_args()
    key = os.environ.get("MEDILENS_HMAC_KEY")
    if not key or len(key) < 32:
        print("MEDILENS_HMAC_KEY missing or shorter than 32 chars", file=sys.stderr)
        return 2
    k = key.encode()
    n = 0
    if a.src.endswith(".jsonl"):
        with open(a.src, encoding="utf-8") as fi, open(a.dst, "w", encoding="utf-8") as fo:
            for line in fi:
                if line.strip():
                    fo.write(
                        json.dumps(
                            transform(json.loads(line), k, a.hash, set(a.drop), a.birth_year_band),
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    n += 1
    else:
        with open(a.src, newline="", encoding="utf-8") as fi:
            reader = csv.DictReader(fi)
            fields = [f for f in reader.fieldnames or [] if f not in set(a.drop)]
            with open(a.dst, "w", newline="", encoding="utf-8") as fo:
                w = csv.DictWriter(fo, fieldnames=fields)
                w.writeheader()
                for row in reader:
                    w.writerow(transform(row, k, a.hash, set(a.drop), a.birth_year_band))
                    n += 1
    print(f"wrote {n} records to {a.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
