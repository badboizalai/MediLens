"""Render REPORT.md from results (numbers only from measured runs; no fabricated values)."""

from __future__ import annotations

from pathlib import Path


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.2f}%"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out + [""]


def recommendation(results: list[dict]) -> str:
    ok = [r for r in results if r["status"] == "ok"]
    if not ok:
        return "No engine produced measurements; no recommendation can be made."
    best = min(ok, key=lambda r: r["cer"]["overall"])
    fastest = min(ok, key=lambda r: r["latency_s"]["mean"])
    text = (
        f"On this set, **{best['engine']}** has the lowest overall CER "
        f"({pct(best['cer']['overall'])}); **{fastest['engine']}** has the lowest mean latency "
        f"({fastest['latency_s']['mean']:.2f} s/page)."
    )
    skipped = [r["engine"] for r in results if r["status"] != "ok"]
    if skipped:
        text += f" Not compared (not run): {', '.join(skipped)}."
    return text


def render(results: list[dict], meta: dict, commentary: str = "") -> str:
    ok = [r for r in results if r["status"] == "ok"]
    lines = ["# OCR bake-off report: golden-v0", ""]
    lines += [
        f"Dataset: `{meta['golden']}`, {meta['pages']} pages (one per record; degraded variant "
        "when the record has one), 100% synthetic. Reference = text drawn by the generator. "
        "CER = (S+D+I)/N chars, micro-averaged, NFC-normalised, whitespace collapsed. "
        f"Hardware: {meta['hardware']}. Python {meta['python']}.",
        "",
        "## Summary",
        "",
    ]
    rows = []
    for r in results:
        if r["status"] == "ok":
            rows.append(
                [
                    r["engine"],
                    "ok",
                    pct(r["cer"]["overall"]),
                    f"{r['latency_s']['mean']:.2f}",
                    f"{r['latency_s']['p95']:.2f}",
                    f"{r['usd_per_doc']:.5f}",
                ]
            )
        else:
            rows.append([r["engine"], "not run", "-", "-", "-", "-"])
    lines += _table(
        ["Engine", "Status", "CER overall", "Latency mean (s/page)", "p95 (s)", "USD/doc"], rows
    )
    lines += [
        "USD/doc basis: " + "; ".join(f"{r['engine']}: {r['cost_basis']}" for r in ok) + ".",
        "",
    ]
    if ok:
        lines += ["## CER by language", ""]
        langs = sorted({k for r in ok for k in r["cer"]["by_lang"]})
        lines += _table(
            ["Engine", *langs],
            [[r["engine"], *[pct(r["cer"]["by_lang"].get(k)) for k in langs]] for r in ok],
        )
        lines += ["## CER by quality", ""]
        quals = [
            q for q in ("good", "medium", "poor") if any(q in r["cer"]["by_quality"] for r in ok)
        ]
        lines += _table(
            ["Engine", *quals],
            [[r["engine"], *[pct(r["cer"]["by_quality"].get(k)) for k in quals]] for r in ok],
        )
    skipped = [r for r in results if r["status"] != "ok"]
    if skipped:
        lines += ["## Not run", ""]
        lines += [f"- **{r['engine']}**: {r['error']}" for r in skipped] + [""]
    lines += ["## Recommendation", "", recommendation(results), ""]
    lines += [
        "Caveats: golden-v0 is synthetic, one template per Unit, rendered in a clean sans font with "
        "mild degradations and no handwriting, stamps or perspective warp, so all numbers are "
        "optimistic versus real Vietnamese records. 50 pages: use for ranking and regression only, "
        "not release claims. Latency is wall-clock on the machine above (not the production "
        "worker) after one warm-up page; compute USD is an assumed container price, not an AWS "
        "quote. Handwriting is untested; a real-like redacted set is needed before deciding.",
        "",
    ]
    if commentary.strip():
        lines += ["## Observations", "", commentary.strip(), ""]
    return "\n".join(lines)


def write(path: Path, results: list[dict], meta: dict, commentary: str = "") -> None:
    path.write_text(render(results, meta, commentary), encoding="utf-8")
