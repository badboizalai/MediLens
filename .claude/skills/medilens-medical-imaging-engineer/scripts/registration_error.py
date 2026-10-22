#!/usr/bin/env python3
"""Target registration error (TRE) from landmark pairs.

Usage: python registration_error.py landmarks.csv [--max-mm 15]

CSV columns: landmark, x_reg, y_reg, z_reg, x_ref, y_ref, z_ref (millimetres;
registered patient landmark vs template landmark). Prints per-landmark error,
mean, median, max and share under the limit. PASS when the mean is below the
limit (plan 27.3); a warning is printed for any single landmark above 2x limit.
"""
import argparse
import csv
import math
import statistics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--max-mm", type=float, default=15.0)
    a = ap.parse_args()
    errs = []
    with open(a.csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = math.dist((float(r["x_reg"]), float(r["y_reg"]), float(r["z_reg"])),
                          (float(r["x_ref"]), float(r["y_ref"]), float(r["z_ref"])))
            errs.append((r["landmark"], d))
    if not errs:
        raise SystemExit("no landmarks")
    for name, d in errs:
        flag = "  <-- > 2x limit" if d > 2 * a.max_mm else ""
        print(f"{name:<24} {d:7.2f} mm{flag}")
    vals = [d for _n, d in errs]
    mean, med, mx = statistics.mean(vals), statistics.median(vals), max(vals)
    share = sum(1 for v in vals if v < a.max_mm) / len(vals)
    print(f"n={len(vals)} mean={mean:.2f} median={med:.2f} max={mx:.2f} mm; under {a.max_mm} mm: {share:.0%}")
    ok = mean < a.max_mm
    print("RESULT:", "PASS" if ok else "FAIL (fall back to template)")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
