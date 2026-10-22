#!/usr/bin/env python3
"""Choose the Tier M → Tier L escalation threshold from an eval CSV.

Usage: python threshold_tuner.py eval.csv [--target 0.92] [--cost-m 0.0068] [--cost-l 0.024] [--step 0.02]

CSV columns: item_id, m_confidence (0..1), m_correct (0/1), l_correct (0/1).
For each threshold t, items with m_confidence < t are escalated to Tier L.
Prints accuracy, escalation rate and cost per item; recommends the smallest
escalation that reaches the target accuracy (or the best accuracy if none do).
Use the dev set, never the golden set.
"""
import argparse
import csv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--target", type=float, default=0.92)
    ap.add_argument("--cost-m", type=float, default=0.0068)
    ap.add_argument("--cost-l", type=float, default=0.024)
    ap.add_argument("--step", type=float, default=0.02)
    a = ap.parse_args()
    rows = []
    with open(a.csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append((float(r["m_confidence"]), int(r["m_correct"]), int(r["l_correct"])))
    n = len(rows)
    if not n:
        raise SystemExit("empty eval file")
    results = []
    t = 0.0
    while t <= 1.0 + 1e-9:
        esc = [r for r in rows if r[0] < t]
        keep = [r for r in rows if r[0] >= t]
        acc = (sum(r[1] for r in keep) + sum(r[2] for r in esc)) / n
        rate = len(esc) / n
        cost = a.cost_m + rate * a.cost_l
        results.append((round(t, 4), acc, rate, cost))
        t += a.step
    print(f"items={n} target={a.target}  (M-only accuracy={sum(r[1] for r in rows) / n:.3f}, L-only={sum(r[2] for r in rows) / n:.3f})")
    print(" thresh  accuracy  escalation  usd/item")
    for t, acc, rate, cost in results:
        print(f"  {t:4.2f}    {acc:.3f}     {rate:6.1%}    {cost:.5f}")
    ok = [r for r in results if r[1] >= a.target]
    if ok:
        best = min(ok, key=lambda r: (r[2], -r[1]))
        print(f"RECOMMEND threshold {best[0]:.2f}: accuracy {best[1]:.3f}, escalation {best[2]:.1%}, {best[3]:.5f} USD/item")
        if best[2] > 0.15:
            print("WARNING escalation > 15% — improve the Tier M prompt/schema before accepting this cost")
    else:
        best = max(results, key=lambda r: (r[1], -r[2]))
        print(f"TARGET NOT REACHED; best accuracy {best[1]:.3f} at threshold {best[0]:.2f} (escalation {best[2]:.1%})")


if __name__ == "__main__":
    main()
