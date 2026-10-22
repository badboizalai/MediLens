# Gold Model and Metric Definitions

## Facts
- `fact_document_processing` (grain: document): document_key, user_pseudo_id, unit_key, date_key, doc_type, pages, status_final, time_to_extract_s, time_to_confirm_s, ocr_engine, model_version_key, prompt_version_key, cost_usd.
- `fact_field_extraction` (grain: field per run): run_key, unit_key, field_path, confidence_bucket, was_corrected, correction_type (wrong_value | missing | extra), match_exact, match_fuzzy.
- `fact_user_activity` (grain: event): user_pseudo_id, date_key, event_type, session_id, device_class.
- `fact_explain_query` (grain: question): date_key, unit_key, intents, guardrail_triggered, citations_count, latency_ms, tokens_in, tokens_out, feedback.

## Dimensions
`dim_date`, `dim_unit`, `dim_region`, `dim_doc_type`, `dim_model_version`, `dim_prompt_version`, `dim_device_class`.

## Metrics (define once)
```yaml
metrics:
  - name: activation_rate_7d
    description: Share of new users who confirm >= 1 document within 7 days of sign-up
    formula: count_distinct(users with first_confirm_at <= signup_at + 7d) / count_distinct(new users)
    grain: signup_week
    owner: product-manager
  - name: review_completion_rate
    formula: confirmed documents / extracted documents
    grain: day, unit
  - name: correction_rate
    formula: sum(was_corrected) / count(fields)
    grain: day, unit, model_version
    owner: ai-ml-engineer
  - name: time_to_first_insight_p50
    formula: p50(first_viewer_view_at - first_upload_at)
  - name: cost_per_document_usd
    formula: sum(cost_usd) / count(documents)
  - name: guardrail_trigger_rate
    formula: count(guardrail_triggered) / count(questions)
```
