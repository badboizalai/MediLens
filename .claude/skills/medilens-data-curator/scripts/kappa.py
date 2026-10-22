#!/usr/bin/env python3
"""Cohen's kappa between two annotators.

Usage: python kappa.py labels.csv --a annotator_a --b annotator_b [--item item_id]

The CSV has one row per item with a column per annotator (labels as text).
Rows where either label is empty are skipped. Prints observed agreement,
expected agreement, kappa, a confusion table and the disagreeing item ids.
Interpretation used by MediLens: >= 0.8 good, 0.6-0.8 adjudicate, < 0.6 retrain.
"""

import argparse
import csv
from collections import Counter


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        raise ValueError("no comparable rows")
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    kappa = 1.0 if pe == 1 else (po - pe) / (1 - pe)
    return po, pe, kappa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--item", default="item_id")
    args = ap.parse_args()
    pairs, ids, disagree = [], [], []
    with open(args.csv, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            a, b = (row.get(args.a) or "").strip(), (row.get(args.b) or "").strip()
            if not a or not b:
                continue
            pairs.append((a, b))
            ids.append(row.get(args.item, ""))
            if a != b:
                disagree.append(row.get(args.item, "?"))
    po, pe, k = cohen_kappa(pairs)
    labels = sorted({x for p in pairs for x in p})
    print(f"items={len(pairs)} observed={po:.3f} expected={pe:.3f} kappa={k:.3f}")
    verdict = (
        "good (>= 0.8)" if k >= 0.8 else ("adjudicate (0.6-0.8)" if k >= 0.6 else "retrain (< 0.6)")
    )
    print("verdict:", verdict)
    width = max(len(s) for s in labels + ["a\\b"]) + 2
    print("".ljust(width) + "".join(l.ljust(width) for l in labels))
    for la in labels:
        print(
            la.ljust(width)
            + "".join(
                str(sum(1 for a, b in pairs if a == la and b == lb)).ljust(width) for lb in labels
            )
        )
    if disagree:
        print("disagreements:", ", ".join(disagree[:50]) + (" …" if len(disagree) > 50 else ""))


if __name__ == "__main__":
    main()
