-- Full rebuild, one transaction. Aggregates only: no values, text or profile ids leave OLTP.
DELETE FROM analytics.mart_run_metrics;
INSERT INTO analytics.mart_run_metrics
WITH r AS (
  SELECT r.id, r.document_id, r.created_at::date AS day, coalesce(r.model, 'unknown') AS model,
         coalesce(r.prompt_version, 'unknown') AS prompt_version, coalesce(r.cost_usd, 0) AS cost_usd
  FROM clinical.extraction_runs r WHERE r.deleted_at IS NULL
), f AS (
  SELECT run_id, count(*) AS total,
         count(*) FILTER (WHERE confirmed_at IS NOT NULL) AS reviewed,
         count(*) FILTER (WHERE confirmed_at IS NOT NULL AND user_value IS NOT NULL
                          AND user_value IS DISTINCT FROM value) AS corrected
  FROM clinical.extraction_fields WHERE deleted_at IS NULL GROUP BY run_id
)
SELECT r.day, r.model, r.prompt_version, count(*)::int, count(DISTINCT r.document_id)::int,
       sum(r.cost_usd), sum(r.cost_usd) / nullif(count(DISTINCT r.document_id), 0),
       coalesce(sum(f.total), 0)::int, coalesce(sum(f.reviewed), 0)::int,
       coalesce(sum(f.corrected), 0)::int,
       sum(f.corrected)::float8 / nullif(sum(f.reviewed), 0),
       sum(f.reviewed)::float8 / nullif(sum(f.total), 0)
FROM r LEFT JOIN f ON f.run_id = r.id GROUP BY 1, 2, 3;

DELETE FROM analytics.mart_doc_status;
INSERT INTO analytics.mart_doc_status
SELECT d.uploaded_at::date, count(*)::int,
       count(*) FILTER (WHERE status = 'needs_retake')::int,
       count(*) FILTER (WHERE status = 'rejected')::int,
       count(*) FILTER (WHERE status = 'failed')::int,
       count(*) FILTER (WHERE status = 'needs_retake')::float8 / count(*),
       count(*) FILTER (WHERE status = 'rejected')::float8 / count(*),
       count(*) FILTER (WHERE status = 'failed')::float8 / count(*),
       -- proxy: no status history table; updated_at of a doc still in needs_review ~ arrival time
       percentile_cont(0.5) WITHIN GROUP (ORDER BY extract(epoch FROM d.updated_at - d.uploaded_at))
         FILTER (WHERE status = 'needs_review'),
       percentile_cont(0.95) WITHIN GROUP (ORDER BY extract(epoch FROM d.updated_at - d.uploaded_at))
         FILTER (WHERE status = 'needs_review')
FROM clinical.documents d WHERE d.deleted_at IS NULL GROUP BY 1;

INSERT INTO analytics.mart_refresh (id, refreshed_at) VALUES (1, now())
ON CONFLICT (id) DO UPDATE SET refreshed_at = excluded.refreshed_at;
