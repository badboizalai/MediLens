# OCR bake-off report: golden-v0

Dataset: `../golden-v0`, 85 page images (every variant of every record: clean, degraded, handwriting, perspective), 100% synthetic. Reference = text drawn by the generator. CER = (S+D+I)/N chars, micro-averaged, NFC-normalised, whitespace collapsed. Hardware: x86_64, CPU only, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.43. Python 3.10.22.

## Summary

| Engine | Status | CER overall | Latency mean (s/page) | p95 (s) | USD/doc |
|---|---|---|---|---|---|
| paddle | ok | 15.63% | 0.34 | 0.44 | 0.00001 |
| vietocr | ok | 4.40% | 1.84 | 2.54 | 0.00005 |
| llm-vision | not run | - | - | - | - |

USD/doc basis: paddle: cpu time at 0.1 USD/h (assumed); vietocr: cpu time at 0.1 USD/h (assumed).

## CER by language

| Engine | en | vi |
|---|---|---|
| paddle | 4.97% | 18.28% |
| vietocr | 2.71% | 4.82% |

## CER by image variant

| Engine | clean (n=50) | degraded (n=25) | handwriting (n=5) | perspective (n=5) |
|---|---|---|---|---|
| paddle | 12.35% | 22.63% | 15.31% | 13.21% |
| vietocr | 2.85% | 7.61% | 3.12% | 4.64% |

## CER by quality

| Engine | good | medium | poor |
|---|---|---|---|
| paddle | 12.10% | 16.09% | 21.09% |
| vietocr | 2.79% | 5.03% | 5.75% |

## Not run

- **llm-vision**: ANTHROPIC_API_KEY not set

## Recommendation

On this set, **vietocr** has the lowest overall CER (4.40%); **paddle** has the lowest mean latency (0.34 s/page). Not compared (not run): llm-vision.

Caveats: golden-v0 is synthetic, one template per Unit, rendered in a clean sans font with mild degradations; the handwriting variant is typeface jitter (not pen strokes) and the perspective variant a flat 4-point warp; no stamps. All numbers are optimistic versus real Vietnamese records. Handwriting/perspective groups have 5 pages each: indicative only. Pages are not independent (variants share a record's text). Use for ranking and regression only, not release claims. Latency is wall-clock on the machine above (not the production worker) after one warm-up page; compute USD is an assumed container price, not an AWS quote. Real handwriting is untested; a real-like redacted set is needed before deciding.

## Observations

- The `vietocr` pipeline is PaddleOCR text detection plus VietOCR (`vgg_transformer`) recognition per line crop, so its latency includes detection and is higher than `paddle` alone. VietOCR is a recogniser only and needs a detector.
- `paddle` uses PP-OCRv3 latin recognition (`lang="vi"`); on spot-checked pages its output drops many Vietnamese diacritics and some spaces (for example "Benh vien Thu Nghiem"), which dominates its CER on Vietnamese pages. English pages are much closer.
- CER rises from good to medium to poor for both engines, as expected from the blur/skew/shadow degradations.
- `llm-vision` (Anthropic) adapter is implemented behind the same Protocol but was not run: no API key is available locally. Run with `ANTHROPIC_API_KEY` set; only synthetic images are ever sent. Model id (default `claude-haiku-5-5`) and token prices are read from `bakeoff/config.toml`; the prices there are assumptions to verify before quoting cost.
- All 85 page images are scored (clean, degraded, handwriting, perspective); per-page rows (doc_id, unit, lang, quality, variant, engine, cer, latency_s) are in `results/golden-v0.json`. Handwriting/perspective are simulated and n=5 each, so those columns are indicative only.
- CPU latency was measured on a 32-thread WSL2 host and will differ on the 2 vCPU production worker.

Reproduce:

```
cd ml/eval/ocr_bakeoff
uv sync --python 3.10 --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match
uv run python -m bakeoff --engines paddle,vietocr,llm-vision --golden ../golden-v0
```

Reference text (`reference/golden-v0.reference.jsonl`) is regenerated from the seeded generator with `uv run python -m bakeoff.make_reference --golden ../golden-v0`.
