-- models/gold/fact_field_extraction.sql
-- Grain: one row per extracted field per extraction run.
{{ config(
    materialized='incremental',
    unique_key=['run_key', 'field_path'],
    partition_by=['dt'],
    on_schema_change='fail'
) }}

with fields as (
    select
        f.run_id                       as run_key,
        f.field_path,
        r.unit_code,
        r.model_version,
        r.prompt_version,
        case
            when f.confidence >= 0.9 then '0.9+'
            when f.confidence >= 0.7 then '0.7-0.9'
            else '<0.7'
        end                            as confidence_bucket,
        (f.user_value is not null and f.user_value <> f.ai_value) as was_corrected,
        cast(r.created_at as date)     as dt
    from {{ ref('silver_extraction_fields') }} f
    join {{ ref('silver_extraction_runs') }} r on r.run_id = f.run_id
    {% if is_incremental() %}
    where cast(r.created_at as date) >= (select max(dt) - interval '3' day from {{ this }})
    {% endif %}
)
select * from fields

-- models/gold/schema.yml (tests)
-- - name: fact_field_extraction
--   columns:
--     - name: run_key
--       tests: [not_null]
--     - name: confidence_bucket
--       tests:
--         - accepted_values: {values: ['0.9+', '0.7-0.9', '<0.7']}
