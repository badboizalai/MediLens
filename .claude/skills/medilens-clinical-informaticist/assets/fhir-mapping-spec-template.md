# FHIR mapping spec — <resource / feature>

| Field | Value |
| --- | --- |
| Direction | import / export |
| FHIR version | R4 |
| Source → target | |

| FHIR path | MediLens field | Transform | Required | Test case |
| --- | --- | --- | --- | --- |

Edge cases: missing codes · multiple codings · unknown units · patient_reported · conflicts (BR-044)
Validation: fhir_bundle_check.py + official validator in CI
