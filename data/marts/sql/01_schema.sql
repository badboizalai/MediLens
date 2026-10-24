CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.eval_scores (
  report_date date NOT NULL,
  prompt_version text NOT NULL,
  cer real NOT NULL,
  field_f1 real NOT NULL,
  PRIMARY KEY (report_date, prompt_version)
);

CREATE TABLE IF NOT EXISTS analytics.mart_run_metrics (
  day date NOT NULL,
  model text NOT NULL,
  prompt_version text NOT NULL,
  runs int NOT NULL,
  docs int NOT NULL,
  cost_usd numeric(12,6) NOT NULL,
  usd_per_doc numeric(12,6),
  fields_total int NOT NULL,
  fields_reviewed int NOT NULL,
  fields_corrected int NOT NULL,
  correction_rate double precision,
  confirm_rate double precision,
  PRIMARY KEY (day, model, prompt_version)
);

CREATE TABLE IF NOT EXISTS analytics.mart_doc_status (
  day date NOT NULL PRIMARY KEY,
  docs int NOT NULL,
  needs_retake int NOT NULL,
  rejected int NOT NULL,
  failed int NOT NULL,
  needs_retake_rate double precision NOT NULL,
  rejected_rate double precision NOT NULL,
  failed_rate double precision NOT NULL,
  latency_p50_s double precision,
  latency_p95_s double precision
);

CREATE TABLE IF NOT EXISTS analytics.mart_refresh (
  id int PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  refreshed_at timestamptz NOT NULL
);
