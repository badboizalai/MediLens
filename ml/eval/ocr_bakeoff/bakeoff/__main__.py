"""CLI: uv run python -m bakeoff --engines paddle,vietocr --golden ml/eval/golden-v0"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

from bakeoff import report
from bakeoff.engines import ENGINES
from bakeoff.golden import DEFAULT_REFERENCE, load_pages
from bakeoff.runner import run_engine

HERE = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="bakeoff")
    ap.add_argument("--engines", default="paddle,vietocr,llm-vision")
    ap.add_argument("--golden", type=Path, required=True)
    ap.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    ap.add_argument("--out", type=Path, default=HERE / "results" / "golden-v0.json")
    ap.add_argument("--report", type=Path, default=HERE / "REPORT.md")
    ap.add_argument("--commentary", type=Path, default=HERE / "reference" / "commentary.md")
    ap.add_argument("--limit", type=int, default=0, help="first N pages only (smoke test)")
    a = ap.parse_args(argv)

    pages = load_pages(a.golden, a.reference)
    if a.limit:
        pages = pages[: a.limit]
    results = []
    for name in a.engines.split(","):
        if name not in ENGINES:
            raise SystemExit(f"unknown engine {name!r}; choose from {sorted(ENGINES)}")
        print(f"running {name} on {len(pages)} pages ...", flush=True)
        res = run_engine(ENGINES[name](), pages)
        print(f"  {res['status']}" + (f": {res['error']}" if res["status"] != "ok" else ""))
        results.append(res)

    meta = {
        "golden": str(a.golden),
        "pages": len(pages),
        "python": platform.python_version(),
        "hardware": f"{platform.processor() or platform.machine()}, CPU only, {platform.platform()}",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps({"meta": meta, "results": results}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    commentary = a.commentary.read_text(encoding="utf-8") if a.commentary.exists() else ""
    report.write(a.report, results, meta, commentary)
    print(f"wrote {a.out} and {a.report}")


if __name__ == "__main__":
    main()
