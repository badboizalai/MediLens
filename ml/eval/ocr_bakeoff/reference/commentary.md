- The `vietocr` pipeline is PaddleOCR text detection plus VietOCR (`vgg_transformer`) recognition per line crop, so its latency includes detection and is higher than `paddle` alone. VietOCR is a recogniser only and needs a detector.
- `paddle` uses PP-OCRv3 latin recognition (`lang="vi"`); on spot-checked pages its output drops many Vietnamese diacritics and some spaces (for example "Benh vien Thu Nghiem"), which dominates its CER on Vietnamese pages. English pages are much closer.
- CER rises from good to medium to poor for both engines, as expected from the blur/skew/shadow degradations.
- `llm-vision` (Anthropic) adapter is implemented behind the same Protocol but was not run: no API key is available locally. Run with `ANTHROPIC_API_KEY` set; only synthetic images are ever sent. Token prices are illustrative defaults (override with `BAKEOFF_LLM_USD_IN_PER_M` / `BAKEOFF_LLM_USD_OUT_PER_M`; model via `BAKEOFF_LLM_MODEL`).
- CPU latency was measured on a 32-thread WSL2 host and will differ on the 2 vCPU production worker.

Reproduce:

```
cd ml/eval/ocr_bakeoff
uv sync --python 3.10 --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match
uv run python -m bakeoff --engines paddle,vietocr,llm-vision --golden ../golden-v0
```

Reference text (`reference/golden-v0.reference.jsonl`) is regenerated from the seeded generator with `uv run python -m bakeoff.make_reference --golden ../golden-v0`.
