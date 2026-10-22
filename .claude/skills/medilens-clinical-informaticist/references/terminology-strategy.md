# Terminology strategy

| Domain | System | Version / source | Licence | MediLens use | Update |
| --- | --- | --- | --- | --- | --- |
| Conditions | ICD-10 (Vietnam Ministry of Health list) | MoH-issued list | State document | Condition.code; Unit `conditions[]` | When MoH updates |
| Labs / observations | LOINC | Regenstrief release | Free with registration and terms | Observation.code | Twice yearly releases; review annually |
| Clinical findings / body structures | SNOMED CT | International edition | Non-member country: licence via SNOMED International MLDS (fee by World Bank class, may be waived) | Only after licence; v1 uses ICD-10 + own dictionary | — |
| Teeth | FDI two-digit notation (ISO 3950) | Standard | Free to use | `tooth_xx` regions | Stable |
| Units | UCUM | Regenstrief | Free | Observation.valueQuantity.code | Stable |
| Anatomy references | FMA (via BodyParts3D) / SNOMED body structure | — | CC BY-SA (FMA-based assets) | `region` standard_code | With asset updates |
| Imaging | DICOM | NEMA | Free | v2 ImagingStudy | — |

Rules
- Pin versions in the reference-data load (data engineer) and record them in the Dataset/Licence registers.
- Keep VI and EN display names; Vietnamese abbreviations live in the BA/AI glossary (e.g., THA = tăng huyết áp, ĐTĐ = đái tháo đường).
- Mapping precision: exact > broader (parent code) > none. Never map to a narrower code than the text supports.
