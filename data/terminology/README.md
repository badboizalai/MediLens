# data/terminology

Owner: clinical-informaticist (reviewers: data-curator, 3d-medical-artist). Task S5-T48.

| Item | What |
| --- | --- |
| `region-tree.v1.yaml` | `region_code` tree for dental, cardiology, oncology. Fields: `region_code`, `parent`, `name_vi`, `name_en`, `laterality`, `svg_id`, `mesh_id`, `std_code`, `unit`. |
| `fdi.csv` | FDI table, 52 teeth (permanent 11-48, deciduous 51-85). Generated: `python -m loaders.fdi` from this folder. |
| `dental-terms.v1.yaml` | Dental VI/EN plain-language terms (S8-T77): `term_id`, `vi`, `en`, `abbrev`, `region_hint`, `icd10`. Source: own work, no licensed text. Loader: `loaders/dental.py`. |
| `loaders/` | ICD-10 (MoH VN, LIC-002) and LOINC (LIC-003) loaders. |
| `tests/` | `uv run pytest data/terminology/tests` (not in default `testpaths`). |

## Rules
- Laterality is the patient's own side. `_r` => right, `_l` => left; a child never contradicts a left/right parent. Unknown side of a paired organ is shown at organ level of both sides, never guessed.
- `std_code` stays empty: SNOMED CT is not licensed. `svg_id`/`mesh_id` are null until the 3D artist binds assets (names must equal `region_code`).
- Teeth in the tree are generated from `fdi.csv`; a test keeps them in sync. Edit the generator, not the tree rows by hand.
- `metastatic_site: true` marks common metastatic locations (liver, lung, bone, brain, adrenal) for viewer wording; it is not a finding.

## Loaders
The loaders read a **local file the owner provides** (never committed; no real code lists live in this repo). They first check `data/license-register.csv` and **refuse unless `decision == approved`**. LIC-002 and LIC-003 are currently `needs-verification`, so loading fails with `LicenceNotApproved`.

- ICD-10: CSV `code,title_vi[,title_en]`, pattern `^[A-Z]\d{2}(\.[0-9A-Z]{1,2})?$`.
- LOINC: CSV `loinc_num,long_common_name`, mod-10 check digit validated.
- Duplicates and bad headers raise `InvalidCodeFile`.

Format checks are reused from `.claude/skills/medilens-clinical-informaticist/scripts/fhir_bundle_check.py`. Test fixtures in `tests/fixtures/` are tiny synthetic rows (titles start with `SYNTHETIC`), not real lists.

## Dental terms and ICD-10
`dental-terms.v1.yaml` is own-authored (no external source). `icd10` is empty for every term: LIC-002 is `needs-verification` (gate G1-D). The loader calls the same licence gate as the ICD-10 loader when `icd10` is set, so filling it fails with `LicenceNotApproved` until approval. Only code identifiers (e.g. K02) may ever go there, never titles. `region_hint` must exist in `region-tree.v1.yaml` or be empty.
