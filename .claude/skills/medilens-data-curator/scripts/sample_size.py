#!/usr/bin/env python3
"""Evaluation sample size for a proportion (accuracy/F1 proxy).

Usage: python sample_size.py [--p 0.85] [--e 0.05] [--conf 0.95] [--strata 1] [--population N]

n = z^2 * p(1-p) / e^2, optional finite-population correction
n_adj = n / (1 + (n - 1) / N). Prints per-stratum and total sizes.
"""
import argparse
import math

Z = {0.80: 1.2816, 0.90: 1.6449, 0.95: 1.96, 0.98: 2.3263, 0.99: 2.5758}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.85, help="expected proportion (e.g. accuracy)")
    ap.add_argument("--e", type=float, default=0.05, help="margin of error (half-width)")
    ap.add_argument("--conf", type=float, default=0.95, choices=sorted(Z))
    ap.add_argument("--strata", type=int, default=1)
    ap.add_argument("--population", type=int, default=0)
    a = ap.parse_args()
    z = Z[a.conf]
    n = z * z * a.p * (1 - a.p) / (a.e * a.e)
    if a.population:
        n = n / (1 + (n - 1) / a.population)
    per = math.ceil(n)
    print(f"z={z} p={a.p} e=±{a.e} conf={a.conf}: n_raw={n:.1f} → {per} per stratum")
    print(f"strata={a.strata}: total {per * a.strata}")
    print("Rule of thumb: keep >= 30 items per subgroup used for bias checks.")


if __name__ == "__main__":
    main()
