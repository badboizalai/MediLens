#!/usr/bin/env python3
"""Error budget and burn-rate calculator.

Usage:
    python error_budget.py --slo 0.995 --good 991200 --total 1000000 [--window-days 30] [--elapsed-days 12]
    python error_budget.py --slo 0.995 --burn --bad-rate 0.072      # burn rate of a short window

Outputs remaining budget and whether the budget will be exhausted before the window ends.
"""
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slo", type=float, required=True, help="e.g. 0.995")
    ap.add_argument("--good", type=float)
    ap.add_argument("--total", type=float)
    ap.add_argument("--window-days", type=float, default=30)
    ap.add_argument("--elapsed-days", type=float)
    ap.add_argument("--burn", action="store_true")
    ap.add_argument("--bad-rate", type=float, help="observed error ratio in a window")
    a = ap.parse_args()
    allowed = 1 - a.slo

    if a.burn:
        rate = a.bad_rate / allowed
        hours_to_exhaust = (a.window_days * 24) / rate if rate else float("inf")
        print(f"burn rate: {rate:.1f}x  (allowed error ratio {allowed:.4f})")
        print(f"at this rate the 30-day budget is gone in {hours_to_exhaust:.1f} h")
        print("page (fast burn)" if rate >= 14.4 else "page (slow burn)" if rate >= 6 else "ticket" if rate >= 1 else "ok")
        return

    bad = a.total - a.good
    budget = allowed * a.total
    used = bad / budget if budget else 0
    sli = a.good / a.total if a.total else 1
    print(f"SLI: {sli:.5f}  target: {a.slo}")
    print(f"error budget: {budget:.0f} bad events allowed; used {bad:.0f} ({used * 100:.1f}%); remaining {max(budget - bad, 0):.0f}")
    if a.elapsed_days:
        projected = used * a.window_days / a.elapsed_days
        print(f"projected use by end of window: {projected * 100:.0f}% -> {'EXHAUST' if projected > 1 else 'ok'}")
    policy = "normal delivery" if used < 0.5 else "prioritise reliability" if used < 1 else "FREEZE normal changes"
    print(f"policy: {policy}")


if __name__ == "__main__":
    main()
