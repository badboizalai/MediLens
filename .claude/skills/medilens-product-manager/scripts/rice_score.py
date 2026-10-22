#!/usr/bin/env python3
"""Score a backlog CSV with RICE and print it sorted.

Usage:
    python rice_score.py backlog.csv [--out scored.csv]

CSV columns: id,title,reach,impact,confidence,effort[,override]
- confidence may be 0.5 / 50 / 50%
- override (optional): security | safety | gate | commitment — forces the item
  above scored items in that order.
"""
import argparse
import csv

OVERRIDE_RANK = {"safety": 0, "security": 0, "gate": 1, "commitment": 2}


def to_conf(value: str) -> float:
    v = value.strip().rstrip("%")
    f = float(v)
    return f / 100 if f > 1 else f


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--out")
    a = p.parse_args()

    rows = []
    with open(a.csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            effort = float(r["effort"]) or 0.1
            score = float(r["reach"]) * float(r["impact"]) * to_conf(r["confidence"]) / effort
            r["rice"] = round(score, 2)
            r["_rank"] = OVERRIDE_RANK.get((r.get("override") or "").strip().lower(), 9)
            rows.append(r)

    rows.sort(key=lambda r: (r["_rank"], -r["rice"]))
    print(f"{'#':>3}  {'id':<10} {'rice':>8}  override    title")
    for i, r in enumerate(rows, 1):
        print(f"{i:>3}  {r['id']:<10} {r['rice']:>8}  {(r.get('override') or '-'):<10}  {r['title']}")

    if a.out:
        fields = [k for k in rows[0].keys() if not k.startswith("_")] if rows else []
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
