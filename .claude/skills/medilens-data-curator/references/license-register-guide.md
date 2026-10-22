# License Register guide

## Fields (see assets/license-register-template.csv)
lic_id · source_name · url · licence_name · licence_url · access_type (open/registration/credentialed DUA) · training_allowed (yes/no/unclear) · product_use_allowed · commercial_allowed · redistribution_allowed · share_alike · attribution_text · intended_use · decision (approved / approved with conditions / rejected / pending) · conditions · reviewer · decision_date · next_review · notes

## Reading licences
- NC (non-commercial): no use in a commercial product or a model shipped commercially.
- SA (share-alike): derivatives of the data (and possibly assets) must carry the same licence; decide early whether modified 3D assets will be published under SA.
- ND (no derivatives): cannot modify; usually unsuitable.
- DUA / credentialed access: no redistribution, often purpose-limited; personal credential, cannot be shared with annotators.
- "Open" on an aggregator (e.g., Kaggle) does not override the original source's terms.
- Check separately: right to train, right to use the trained model in the product, attribution placement.

## Known sources (plan section 25.2, checked in 2026 — re-check before use)
| Source | Licence / access | MediLens decision guide |
| --- | --- | --- |
| Synthetic (own) | Own | Approved — primary dev and golden data |
| VinDr-CXR (Vietnam chest X-ray) | PhysioNet Credentialed Health Data License 1.5.0; credentialed account, CITI course, DUA | Learning/internal evaluation only; no redistribution; not for commercial product unless DUA allows |
| MIMIC-IV-Note and other PhysioNet credentialed sets | Credentialed DUA | Learning/internal evaluation only |
| TCIA collections (e.g., LIDC-IDRI) | Mostly CC BY 3.0/4.0; some restricted; head-and-neck sets may be restricted | Approved per collection with citation; check each collection page |
| Medical Segmentation Decathlon | CC BY-SA 4.0 | Approved with share-alike obligations |
| TotalSegmentator dataset on NCI IDC | CC BY 4.0 | Approved with attribution (CT pipeline reference) |
| DENTEX (panoramic dental X-ray) | CC BY-NC-SA 4.0 | Non-commercial learning/evaluation only |
| MTSamples (Kaggle copy) | Listed CC0 but scraped; original terms unclear | Internal learning/evaluation only; never in product |
| ViMQ (Vietnamese medical questions) | No licence published | Contact authors before any use |
| ICD-10 Vietnam MoH list | State document | Approved as master data |
| LOINC | Free with registration and terms | Approved; keep notice |
| SNOMED CT | Licence via MLDS for non-member countries | Not used until licensed |
| BodyParts3D / Z-Anatomy | CC BY-SA | Approved with attribution; SA applies to modified assets |
