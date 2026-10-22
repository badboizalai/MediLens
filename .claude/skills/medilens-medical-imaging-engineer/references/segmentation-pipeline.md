# Segmentation pipeline

- Tool: TotalSegmentator (code Apache-2.0; check the README licence for each task — some extra tasks need a separate licence). Pin the version and weights checksum in the model registry.
- Runtime: GPU queue worker scaled to zero; `--fast` (3 mm) for preview, full resolution for the final mesh; CPU fallback only for tests.
- Inputs: de-identified NIfTI in HU, orientation preserved.
- Outputs: one mask per structure; summary JSON (structures found, voxel counts, volumes in mL).
- QA: volume within plausible range per structure (flag outliers rather than block), single dominant connected component for solid organs, left/right consistency with patient orientation, missing expected organs → note "not in field of view".
- Data for evaluation: TotalSegmentator dataset on NCI IDC (CC BY 4.0) and TCIA collections with permissive licences; 30–50 reference cases (plan 25.1).
- Never derive lesion masks or measurements (BR-042).
