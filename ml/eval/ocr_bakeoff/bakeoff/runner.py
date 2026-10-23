"""Run engines over pages: CER (overall/lang/quality/variant), latency per page, USD per doc."""

from __future__ import annotations

import statistics
import time

from bakeoff.engines import EngineUnavailable, OcrEngine
from bakeoff.golden import Page
from bakeoff.metrics import aggregate, cer_counts

# Illustrative assumption: 2 vCPU / 4 GB container ~ 0.10 USD/h (verify vs AWS Fargate price page).
CPU_USD_PER_HOUR = 0.10


def compute_usd(seconds: float, usd_per_hour: float = CPU_USD_PER_HOUR) -> float:
    return seconds * usd_per_hour / 3600


def percentile(values: list[float], q: float) -> float:
    s = sorted(values)
    return s[min(len(s) - 1, round(q * (len(s) - 1)))]


def run_engine(engine: OcrEngine, pages: list[Page], warmup: bool = True) -> dict:
    try:
        engine.load()
    except EngineUnavailable as e:
        return {"engine": engine.name, "status": "not run", "error": str(e)}
    if warmup and pages:  # first call pays one-off graph/kernel init; exclude it from latency
        engine.recognize(pages[0].image)
    rows, lat, usd, api = [], [], [], False
    for p in pages:
        t0 = time.perf_counter()
        res = engine.recognize(p.image)
        dt = time.perf_counter() - t0
        edits, chars = cer_counts(p.reference, res.text)
        rows.append(
            {
                "doc_id": p.doc_id,
                "unit": p.unit,
                "lang": p.lang,
                "quality": p.quality,
                "variant": p.variant,
                "engine": engine.name,
                "cer": edits / chars if chars else None,
                "latency_s": round(dt, 3),
                "edits": edits,
                "chars": chars,
            }
        )
        lat.append(dt)
        api = api or res.usd is not None
        usd.append(res.usd if res.usd is not None else compute_usd(dt))
    return {
        "engine": engine.name,
        "status": "ok",
        "pages": len(pages),
        "cer": aggregate(rows),
        "latency_s": {
            "mean": statistics.fmean(lat),
            "p50": percentile(lat, 0.5),
            "p95": percentile(lat, 0.95),
        },
        "usd_per_doc": statistics.fmean(usd),  # golden-v0 docs are single page; mean per image
        "cost_basis": "api usage" if api else f"cpu time at {CPU_USD_PER_HOUR} USD/h (assumed)",
        "rows": rows,
    }
