# Extraction JSON Schemas v1

Shared home of the extraction schemas for the 3 Units (`dental`, `cardiology`, `oncology`), promoted from `ml/eval/golden-v0/schemas` (which stays frozen for replay). Draft 2020-12; `$ref`s resolve through `$id` (`https://medilens.local/schemas/<name>.v1.json`), so load all four files into one registry.

Reviewed against `.claude/skills/medilens-ai-ml-engineer/references/extraction-schemas.md`. Changes vs golden-v0:

| Change | Why |
| --- | --- |
| `source` is **required** on `StringField`/`NumberField`/`DateField` (`page` >= 1, exact `quote`) | every value must cite where it came from (review screen, BR-042 faithfulness) |
| `Source.bbox` stays optional, now normalised `[x0,y0,x1,y1]` in 0..1, top-left origin | OCR engines without layout can still validate |
| `confidence` bounded 0..1 on every field (was unbounded on `DateField`) | consistent thresholds in the cascade |
| new `Region` `{region_code, confidence}` on `dental.teeth[]`, `cardiology.diagnoses[]`, `oncology.primary` and `oncology.metastases[]` | `region_code` is the contract with assets and viewer; `null` = unmapped |

Rules: `region_code` must be a code of the Unit region tree (`^[a-z][a-z0-9_]*$`), never invented; the golden-v1 generator emits `tooth_<FDI>` for teeth and `liver` for liver metastases, everything else is `null` until the clinical-informaticist region tree covers it. golden-v0 records validate unchanged against these schemas. Any further change = new `*.v2.json`.

Validate: `uv run --with pillow --with jsonschema --with pytest pytest ml/datasets/synth -q`.
