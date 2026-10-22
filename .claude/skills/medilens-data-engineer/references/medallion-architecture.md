# Medallion Architecture on AWS

## Layers
| Layer | Content | Format | Location | Access |
| --- | --- | --- | --- | --- |
| Source | OLTP tables | PostgreSQL | RDS prod | app roles only; DE read-only replica/role |
| Bronze | Pseudonymised daily extracts / CDC; product events | Parquet, `dt=YYYY-MM-DD` | `s3://<env>-analytics-bronze` | DE |
| Silver | Cleaned, typed, deduped, joined with reference data | Parquet / Iceberg | `s3://<env>-analytics-silver` | DE, AI |
| Gold | Facts/dims, metric tables | Iceberg / Postgres analytics schema | `s3://<env>-analytics-gold` | PO, AI, dashboards |
| ML datasets | Golden/dev/red-team, synthetic | JSONL + images | `s3://<env>-ml-datasets` | AI |
| Vector | Approved article chunks | pgvector | RDS | API |

## AWS services by phase
| Phase | Choice | Why |
| --- | --- | --- |
| MVP | Postgres `analytics` schema + dbt-postgres + scheduled ECS task + Metabase | Minimal moving parts |
| v1.5 | S3 Parquet + Glue Data Catalog + Athena + dbt-athena + Prefect on ECS | Serverless, cheap, separates PHI boundary |
| v2 | Iceberg tables, Firehose for events, Lake Formation column permissions, QuickSight | Governance, fine-grained access |
| Optional | DMS CDC, MWAA (managed Airflow), OpenLineage | Learning enterprise patterns |

## Extraction pattern (daily)
1. ECS task assumes `de-extract` role (read-only DB user limited to selected tables/columns).
2. Query per table with `updated_at >= :last_watermark`; select only allowed columns.
3. Replace `user_id`, `profile_id` with `HMAC_SHA256(key, id)`; drop names/emails/phones; bucket birth year to 5-year bands.
4. Write Parquet to `bronze/<table>/dt=<date>/part-*.parquet`; write `_SUCCESS` with row count + checksum.
5. Update watermark only after success.

## Lake Formation / IAM
- Bronze: only DE role. Silver/Gold: column-level grants; no role can join pseudo IDs back to real IDs (key only in extraction task's secret).
- Athena workgroups: `de`, `analytics` with bytes-scanned limits and result encryption.
