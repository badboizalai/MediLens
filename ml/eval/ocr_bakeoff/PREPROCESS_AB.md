# Preprocess A/B: Canny fallback in `crop_document` (S6-T55)

No OCR engine (PaddleOCR/VietOCR) is installed in the offline worker env, so CER was not re-run. Geometric error is reported instead: mean absolute grey difference between the cropped page and the same record's `_clean` image, resized to the clean size (0 = identical; lower is better). Synthetic only: golden-v0 perspective variants (n=5), and the clean pages re-photographed with a keystone onto a flat desk (n=5 each).

| Case | main (Otsu only) | Canny, no desk check (r1) | Canny + border-step check |
|---|---|---|---|
| golden-v0 perspective variants | 1.7 | 1.7 | 1.7 |
| clean page on dark desk (grey 40) | 2.1 | 2.1 | 2.1 |
| clean page on low-contrast desk (grey 225) | 2.8 | 2.8 | 2.8 |
| full-frame scan with inner table, blank margins | 0.7 | 15.6 | 0.0 |

Numbers re-run in round 2 on the golden-v1 `_clean` pages (n=5; 800x1000 page, mild keystone on a 1600x1200 desk). The earlier 18.1 -> 6.7 low-contrast figures came from a different desk render and could not be reproduced; on this render main is already 2.8, so no low-contrast gain is claimed here beyond the unit test (`test_crop_document_warps_to_upright_page[225]`, flat text page on grey 225).

Round-2 finding: r1 cropped a full-frame scan to its inner bordered table (error 15.6). `_has_step` now accepts a quad only when the median grey just outside its border differs from the one just inside by `MIN_EDGE_STEP`; a table on the same paper has no step, a page on a desk does. The check is on the border step rather than outside-edge density because blank page margins look as empty as a flat desk.

Reading: the existing Otsu quad already handles high-contrast pages (no change, no regression). When Otsu returns the whole frame, the new step rejects frame-sized quads (`MAX_DOC_AREA`) and finds the page from Canny edges instead. The golden-v0 CER by variant stays as in `REPORT.md` (perspective: paddle 13.21%, vietocr 4.64%) because those images take the unchanged path.

Not done: VietOCR for printed lines is S6-T55b (heavy model). Re-run the engine bake-off on a harder perspective set (real desk photos, redacted) before claiming a CER gain.

## BUG-13 follow-up

On two shadowed golden-v0 `poor` degraded pages the Otsu quad was the dark lower half of the frame (flush with the left, right and bottom borders, step check passed), so the crop returned a 1000x610 strip. `crop_document` now skips a quad flush with more than two frame sides. Perspective variants (n=5) are unchanged; CER numbers are in `REPORT.md`.
