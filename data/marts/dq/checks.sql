-- Each row = (check name, offending count). Any count > 0 fails the run.
SELECT 'negative_cost', count(*) FROM analytics.mart_run_metrics WHERE cost_usd < 0
UNION ALL SELECT 'rate_out_of_range', count(*) FROM analytics.mart_run_metrics
  WHERE correction_rate NOT BETWEEN 0 AND 1 OR confirm_rate NOT BETWEEN 0 AND 1
UNION ALL SELECT 'status_rate_out_of_range', count(*) FROM analytics.mart_doc_status
  WHERE needs_retake_rate NOT BETWEEN 0 AND 1 OR rejected_rate NOT BETWEEN 0 AND 1
     OR failed_rate NOT BETWEEN 0 AND 1
UNION ALL SELECT 'eval_out_of_range', count(*) FROM analytics.eval_scores
  WHERE cer < 0 OR field_f1 NOT BETWEEN 0 AND 1
UNION ALL SELECT 'null_day', (SELECT count(*) FROM analytics.mart_run_metrics WHERE day IS NULL)
  + (SELECT count(*) FROM analytics.mart_doc_status WHERE day IS NULL)
UNION ALL SELECT 'run_count_mismatch',
  abs((SELECT coalesce(sum(runs), 0) FROM analytics.mart_run_metrics)
    - (SELECT count(*) FROM clinical.extraction_runs WHERE deleted_at IS NULL))
UNION ALL SELECT 'doc_count_mismatch',
  abs((SELECT coalesce(sum(docs), 0) FROM analytics.mart_doc_status)
    - (SELECT count(*) FROM clinical.documents WHERE deleted_at IS NULL))
UNION ALL SELECT 'stale_refresh', count(*) FROM analytics.mart_refresh
  WHERE refreshed_at < now() - interval '1 hour'
UNION ALL SELECT 'never_refreshed', 1 - count(*) FROM analytics.mart_refresh;
