# Domain ↔ FHIR R4 mapping

| MediLens | FHIR R4 | Key elements | Notes |
| --- | --- | --- | --- |
| PatientProfile | Patient (export only, minimal) | id (opaque), gender, birthDate (year only by default) | No name/identifiers on export unless the user opts in |
| MedicalDocument | DocumentReference | type, date, content.attachment (not embedded by default) | Provenance for findings |
| Encounter | Encounter | period, serviceProvider (display only) | |
| Condition | Condition | code (ICD-10 system `http://hl7.org/fhir/sid/icd-10`), bodySite, recordedDate, evidence.detail → DocumentReference | `patient_reported` → no code, note text, category `problem-list-item` with extension `sourceType` |
| BodyFinding | Condition.bodySite / BodyStructure | location (region crosswalk), laterality qualifier | |
| Observation | Observation | code (LOINC `http://loinc.org`), valueQuantity (UCUM `http://unitsofmeasure.org`), referenceRange (as printed), effectiveDateTime | |
| Procedure | Procedure | code (text or ICD-9-CM/other when present), bodySite, performedDateTime | Surgery history feeds `organ_status` |
| Device | Device + DeviceUseStatement | type, bodySite | Implants/glyphs |
| ImagingStudy (v2) | ImagingStudy | series, modality CT, numberOfInstances | No pixel data in FHIR export |

Import rules: accept Bundle types `collection`, `document`, `searchset`; ignore resource types not in the table (MedicationStatement, AllergyIntolerance… are listed as "not displayed in v1.5"); drop Patient identity fields at the PHI boundary; every imported item gets `sourceType = record`.
Export rules: Bundle `collection`, only confirmed data, internal ids replaced by UUIDs, validated in CI.
