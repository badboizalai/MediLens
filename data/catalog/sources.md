# Data and asset sources (summary of `data/license-register.csv`)

Task S2-T05, drafted 2026-10-23 by Data Curator; Regulatory sign-off pending (gate G1-D). Next review 2027-01-23.
Rule: if a licence term is not certain, status is `needs-verification` and nothing is downloaded or used. Terms quoted from plan section 25.2 are claims to check, not approvals.

| ID | Source | Licence (as stated, unverified unless noted) | Status |
| --- | --- | --- | --- |
| LIC-001 | Synthetic generator (own) | Own | approved |
| LIC-002 | MoH ICD-10 VN | State document | needs-verification |
| LIC-003 | LOINC | LOINC licence (registration) | needs-verification |
| LIC-004 | SNOMED CT | MLDS affiliate licence; none held | needs-verification (not used in v1) |
| LIC-005 | FDI notation | ISO 3950 / unknown | needs-verification |
| LIC-006 | UCUM | UCUM licence | needs-verification |
| LIC-007 | BodyParts3D | CC BY-SA | needs-verification |
| LIC-008 | Z-Anatomy | CC BY-SA | needs-verification |
| LIC-009 | TCIA | Per collection | needs-verification |
| LIC-010 | MTSamples | Kaggle CC0, original terms unclear | needs-verification |
| LIC-011 | DENTEX | CC BY-NC-SA 4.0 | needs-verification |
| LIC-012 | TotalSegmentator dataset | CC BY 4.0 | needs-verification |
| LIC-013 | Medical Segmentation Decathlon | CC BY-SA 4.0 | needs-verification |

## Blocked until verified
- Everything except LIC-001: no download, ingestion into reference tables, training, or shipping.
- LIC-004 SNOMED CT: stays unused until a licence is issued.
- LIC-009 TCIA: add one row per chosen collection first; restricted collections (e.g. some head-and-neck sets) excluded.
- LIC-010 MTSamples and LIC-011 DENTEX: at most internal learning/evaluation; never in the product or golden set. Whether a model trained on DENTEX may ship commercially: assume no.
- LIC-007/008/013 (share-alike): Regulatory must decide the SA scope for derived meshes and trained models.
- LIC-012: also check the separate licence of TotalSegmentator model weights/code.
- Not yet registered (add before any use): VinDr-CXR and other PhysioNet credentialed sets (DUA), ViMQ (no licence published).
