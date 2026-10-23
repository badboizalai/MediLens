# Anatomy mapping eval (S7-T66)

Rules-only `map_region` on golden-v1 (`ml/eval/golden-v1/gold.jsonl`). Input = the source quote of the location field; unit from the doc id.

- Labelled items scored: **186** (metastases 5, teeth 181)
- **Region accuracy: 1.000** (186/186), target >= 0.85 -> PASS
- Errors: 0

## Caveats (honest reading)

- golden-v1 labels regions only for dental teeth (`tooth_<FDI>`) and liver metastases; the other 163 location items have `region_code = null` by design, so region accuracy for cardiology and most oncology sites is **not measurable** yet.
- The scored set is mostly clean synthetic text (`Răng 14`, `Gan`); expect lower accuracy on real OCR output. Laterality, ranges and invalid numbers are covered by unit tests instead.
- Coverage on unlabelled items (not scored): mapper returned a code for 163/163.
