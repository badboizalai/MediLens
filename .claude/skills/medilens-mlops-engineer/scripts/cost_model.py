#!/usr/bin/env python3
"""MediLens AI cost model.

Usage: python cost_model.py config.json [--docs N] [--questions N] [--gpu-hourly USD] [--escalation 0.12]

Computes USD per document and per question from per-step token counts and
tier prices (per million tokens), applies an optional batch share/discount,
prints monthly cost for the given volumes and the self-host break-even volume
for a GPU billed hourly around the clock (720 h per 30-day month).
"""
import argparse
import json

HOURS_PER_MONTH = 720  # 30 days, as in plan 28.4


def step_cost(step, prices):
    p = prices[step["tier"]]
    pin, pout = p["in"] / 1e6, p["out"] / 1e6
    pcache = pin * p.get("cache_read_ratio", 0.1)
    raw = step["in_new"] * pin + step.get("in_cached", 0) * pcache + step["out"] * pout
    return raw * step.get("share", 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--docs", type=int, default=0, help="documents per month")
    ap.add_argument("--questions", type=int, default=0, help="explanation questions per month")
    ap.add_argument("--gpu-hourly", type=float, default=None, help="GPU price per hour for break-even")
    ap.add_argument("--escalation", type=float, default=None, help="override share of the Tier L step")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    prices = cfg["prices_per_million"]
    if a.escalation is not None:
        for s in cfg["document_steps"]:
            if s["tier"] == "L":
                s["share"] = a.escalation

    print("Per-document steps:")
    doc = 0.0
    for s in cfg["document_steps"]:
        c = step_cost(s, prices)
        doc += c
        print(f"  {s['name']:<24} tier {s['tier']}  share {s.get('share', 1):>4.0%}  {c:.6f}")
    gpu_doc = cfg.get("gpu_seconds_per_document", 0) * cfg.get("gpu_hourly_usd", 0) / 3600
    doc += gpu_doc
    bs, bd = cfg.get("batch_share", 0.0), cfg.get("batch_discount", 0.5)
    doc_eff = doc * (1 - bs * bd)
    q = sum(step_cost(s, prices) for s in cfg.get("question_steps", []))
    print(f"USD per document: {doc:.4f}" + (f" (with {bs:.0%} batch at -{bd:.0%}: {doc_eff:.4f})" if bs else ""))
    print(f"USD per question: {q:.4f}")
    if a.docs or a.questions:
        monthly = a.docs * doc_eff + a.questions * q
        print(f"Monthly: {a.docs} docs + {a.questions} questions = {monthly:.2f} USD")
    gpu = a.gpu_hourly if a.gpu_hourly is not None else cfg.get("gpu_hourly_usd") or 0
    if gpu:
        fixed = gpu * HOURS_PER_MONTH
        print(f"Self-host GPU at {gpu} USD/h ≈ {fixed:.0f} USD/month → break-even ≈ {fixed / doc_eff:,.0f} documents/month (before ops effort)")


if __name__ == "__main__":
    main()
