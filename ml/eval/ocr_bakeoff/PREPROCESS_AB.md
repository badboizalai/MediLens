# Preprocess A/B: Canny fallback in `crop_document` (S6-T55)

No OCR engine (PaddleOCR/VietOCR) is installed in the offline worker env, so CER was not re-run. Geometric error is reported instead: mean absolute grey difference between the cropped page and the same record's `_clean` image, resized to the clean size (0 = identical; lower is better). Synthetic only: golden-v0 perspective variants (n=5), and the clean pages re-photographed with a keystone onto a flat desk (n=5 each).

| Case | Before (Otsu only) | After (Otsu, then Canny) |
|---|---|---|
| golden-v0 perspective variants | 1.7 | 1.7 |
| clean page on dark desk (grey 40) | 2.4 | 2.4 |
| clean page on low-contrast desk (grey 225) | 18.1 | 6.7 |

Reading: the existing Otsu quad already handles high-contrast pages (no change, no regression). Low-contrast desks made Otsu return the whole frame; the new step rejects frame-sized quads (`MAX_DOC_AREA`) and finds the page from Canny edges instead. The golden-v0 CER by variant stays as in `REPORT.md` (perspective: paddle 13.21%, vietocr 4.64%) because those images take the unchanged path.

Not done: VietOCR for printed lines is S6-T55b (heavy model). Re-run the engine bake-off on a harder perspective set (real desk photos, redacted) before claiming a CER gain.
