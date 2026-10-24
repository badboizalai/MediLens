# Pipeline metrics mart (S7-T69)

Aggregate-only mart in schema `analytics` (no values, text or profile ids), rebuilt daily from the OLTP
tables by `data/marts/run.py`. Rates use the UTC day of `extraction_runs.created_at` / `documents.uploaded_at`.

| Table | Grain | Metrics |
|---|---|---|
| `mart_run_metrics` | day, model, prompt_version | runs, docs, cost_usd, **usd_per_doc**, fields_total/reviewed/corrected, **correction_rate** (corrected / reviewed), **confirm_rate** (reviewed / total) |
| `mart_doc_status` | day | docs, needs_retake / rejected / failed counts and rates, latency p50/p95 |
| `eval_scores` | report_date, prompt_version | **CER**, **field F1** from offline eval (`ml/eval`), not OLTP |

"Reviewed" = `confirmed_at IS NOT NULL`; "corrected" = reviewed and `user_value` differs from `value`.

## Known gaps
- No `unit` dimension: `extraction_runs` carries no unit; only `conditions.unit_code` (via `source_run_id`) does. Add when runs get a unit.
- Latency upload to needs_review is a proxy (`updated_at - uploaded_at` for docs still in `needs_review`); there is no status-history table. Replace once audit/status events are modelled.
- CER/F1 are an external input: pass `--eval-csv` with columns `report_date,prompt_version,cer,field_f1` (upsert).

## Running
```
cd data && DATABASE_URL=postgresql://... python -m marts.run [--eval-csv eval.csv]
cd data && python -m marts.run --check-only      # DQ + freshness only, no refresh
```
The role needs read access across profiles on `clinical.*` (RLS bypass; a dedicated `analytics_job` role is a follow-up) and CREATE on the DB for `analytics`. Needs `psycopg` (already an api dependency).

## DQ checks (`data/marts/dq/checks.sql`)
non-negative cost, all rates in [0,1], eval CER >= 0 and F1 in [0,1], no NULL day, mart row sums equal source counts (runs, documents), freshness (`refreshed_at` < 1h after refresh; `--check-only` catches a job that stopped running). On any failure the transaction is rolled back (last good mart stays) and the exit code is 1.

## Scheduling (infra wiring is a follow-up, no Terraform here)
Run once a day (e.g. 02:00 ICT) as an ECS scheduled task triggered by an EventBridge rule, using the api image with command `python -m marts.run` and `DATABASE_URL` from Secrets Manager. Alarm on task exit code != 0, and run a second `--check-only` rule a few hours later as the staleness watchdog.
