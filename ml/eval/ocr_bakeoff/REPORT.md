# OCR bake-off report: golden-v0

Dataset: `../golden-v0`, 50 pages (one per record; degraded variant when the record has one), 100% synthetic. Reference = text drawn by the generator. CER = (S+D+I)/N chars, micro-averaged, NFC-normalised, whitespace collapsed. Hardware: x86_64, CPU only, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.43. Python 3.10.22.

## Summary

| Engine | Status | CER overall | Latency mean (s/page) | p95 (s) | USD/doc |
|---|---|---|---|---|---|
| paddle | ok | 17.28% | 0.34 | 0.43 | 0.00001 |
| vietocr | ok | 5.13% | 1.75 | 2.38 | 0.00005 |
| llm-vision | not run | - | - | - | - |

USD/doc basis: paddle: cpu time at 0.1 USD/h (assumed); vietocr: cpu time at 0.1 USD/h (assumed).

## CER by language

| Engine | en | vi |
|---|---|---|
| paddle | 5.54% | 20.32% |
| vietocr | 2.56% | 5.80% |

## CER by quality

| Engine | good | medium | poor |
|---|---|---|---|
| paddle | 11.61% | 20.66% | 27.26% |
| vietocr | 2.50% | 7.42% | 8.06% |

## Not run

- **llm-vision**: ANTHROPIC_API_KEY not set

## Recommendation

On this set, **vietocr** has the lowest overall CER (5.13%); **paddle** has the lowest mean latency (0.34 s/page). Not compared (not run): llm-vision.

Caveats: golden-v0 is synthetic, one template per Unit, rendered in a clean sans font with mild degradations and no handwriting, stamps or perspective warp, so all numbers are optimistic versus real Vietnamese records. 50 pages: use for ranking and regression only, not release claims. Latency is wall-clock on the machine above (not the production worker) after one warm-up page; compute USD is an assumed container price, not an AWS quote. Handwriting is untested; a real-like redacted set is needed before deciding.

## Observations

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
