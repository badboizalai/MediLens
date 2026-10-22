#!/usr/bin/env python3
"""Support statistics from a ticket CSV (MediLens taxonomy).

Usage: python ticket_stats.py tickets.csv [--since YYYY-MM-DD] [--today YYYY-MM-DD] [--g5h]

Prints volume by category and severity, first-response and resolution
percentiles (hours, wall-clock) against SLA targets, open S1/S2, safety and
privacy flagged tickets, and with --g5h the hypercare exit check: no new S1/S2
in the last 14 days and no open safety tickets. Exit 1 if --g5h fails.
"""
import argparse
import csv
from collections import Counter
from datetime import datetime, timedelta

FRT_SLA_H = {"S1": 1, "S2": 4, "S3": 24, "S4": 48}


def parse(ts):
    return datetime.fromisoformat(ts) if ts else None


def pct(values, q):
    if not values:
        return None
    v = sorted(values)
    k = max(0, min(len(v) - 1, round(q * (len(v) - 1))))
    return v[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--since")
    ap.add_argument("--today")
    ap.add_argument("--g5h", action="store_true")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.csv, newline="", encoding="utf-8")))
    since = datetime.fromisoformat(a.since) if a.since else None
    today = datetime.fromisoformat(a.today) if a.today else datetime.now()
    if since:
        rows = [r for r in rows if parse(r["created_at"]) >= since]
    print(f"tickets: {len(rows)}" + (f" since {a.since}" if since else ""))
    print("by category:", dict(Counter(r["category"] for r in rows).most_common()))
    print("by severity:", dict(sorted(Counter(r["severity"] for r in rows).items())))
    frt_breach = 0
    for sev in ("S1", "S2", "S3", "S4"):
        frt = [(parse(r["first_response_at"]) - parse(r["created_at"])).total_seconds() / 3600
               for r in rows if r["severity"] == sev and r.get("first_response_at")]
        res = [(parse(r["resolved_at"]) - parse(r["created_at"])).total_seconds() / 3600
               for r in rows if r["severity"] == sev and r.get("resolved_at")]
        breaches = sum(1 for x in frt if x > FRT_SLA_H[sev])
        frt_breach += breaches
        if frt or res:
            p90f, p90r = pct(frt, 0.9), pct(res, 0.9)
            print(f"  {sev}: FRT p50={pct(frt, 0.5) or 0:.1f}h p90={p90f or 0:.1f}h (SLA {FRT_SLA_H[sev]}h, breaches {breaches}) · "
                  f"resolution p90={p90r if p90r is not None else float('nan'):.1f}h")
    open_s12 = [r["id"] for r in rows if r["severity"] in ("S1", "S2") and r["status"] != "resolved"]
    safety = [r["id"] for r in rows if r.get("safety", "").lower() == "yes"]
    safety_open = [r["id"] for r in rows if r.get("safety", "").lower() == "yes" and r["status"] != "resolved"]
    privacy = [r["id"] for r in rows if r.get("privacy", "").lower() == "yes"]
    print("open S1/S2:", open_s12 or "none")
    print("safety-flagged:", safety or "none", "| open:", safety_open or "none")
    print("privacy-flagged:", privacy or "none")
    if a.g5h:
        window = today - timedelta(days=14)
        recent = [r["id"] for r in rows if r["severity"] in ("S1", "S2") and parse(r["created_at"]) >= window]
        ok = not recent and not safety_open and not open_s12
        print(f"G5-H check (window {window.date()}..{today.date()}): new S1/S2={recent or 'none'}; "
              f"open safety={safety_open or 'none'} → {'PASS' if ok else 'FAIL'}")
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
