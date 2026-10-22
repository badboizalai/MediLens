# Data Quality Rules

| ID | Entity | Dimension | Rule | Severity | Where |
| --- | --- | --- | --- | --- | --- |
| DQ-01 | conditions | Completeness | `icd10_code` not null when status = confirmed | MUST | BE validation + dbt |
| DQ-02 | conditions | Validity | `icd10_code` exists in reference table (current version) | MUST | dbt relationships |
| DQ-03 | body_findings | Validity | `region_code` in unit config regions or = `unmapped` | MUST | BE + dbt |
| DQ-04 | body_findings (dental) | Validity | FDI ∈ 11–18, 21–28, 31–38, 41–48, 51–55, 61–65, 71–75, 81–85 | MUST | worker + dbt |
| DQ-05 | observations | Validity | `unit` is valid UCUM; numeric value within plausible physiological range | MUST/SHOULD | worker + dbt |
| DQ-06 | observations | Consistency | `observed_at` ≥ birth date band start and ≤ now | MUST | dbt |
| DQ-07 | body_findings | Consistency | sex-specific organs consistent with `sex_at_birth` (flag, not block) | SHOULD | dbt |
| DQ-08 | medical_documents | Uniqueness | one active document per `(profile_id, sha256)` | MUST | DB unique index |
| DQ-09 | extraction_fields | Consistency | `user_value` set ⇒ `confirmed_at` set | MUST | dbt |
| DQ-10 | fact_field_extraction | Accuracy proxy | daily correction rate within ±20% of 7-day mean | SHOULD | monitor |
| DQ-11 | gold tables | Timeliness | refreshed by 06:00 ICT | MUST | freshness test |
| DQ-12 | analytics | Reconciliation | gold confirmed documents count = OLTP count ± 0.5% | MUST | reconciliation job |
| DQ-13 | bronze | Privacy | no column matching email/phone/name patterns | MUST | scan |

Severity handling: MUST failure → stop downstream models, alert; SHOULD failure → warning in weekly report.
