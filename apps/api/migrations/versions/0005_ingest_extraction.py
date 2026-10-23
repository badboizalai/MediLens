"""narrow SECURITY DEFINER function so the api-events consumer can ingest extraction results

Same pattern as 0004 (ADR-0006): the function is owned by a NOLOGIN role `extraction_ingest_definer`
let through RLS by explicit policies bound to that role alone (no BYPASSRLS, no app.profile_ids
widening). It may SELECT three columns of clinical.documents and INSERT into extraction_runs /
extraction_fields; it can never UPDATE or DELETE. profile_id is derived from the document row, never
taken from the message. Callers (`api_events_consumer`) get EXECUTE only, no table privileges.
Idempotent on the run id: re-delivery inserts nothing.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-23
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

_SIG = "clinical.ingest_extraction(uuid, uuid, text, text, text, real, numeric, jsonb, jsonb)"
_FUNCTION = """
CREATE FUNCTION clinical.ingest_extraction(p_document_id uuid, p_run_id uuid,
  p_pipeline_version text, p_model text, p_prompt_version text, p_confidence real,
  p_cost_usd numeric, p_raw_output jsonb, p_fields jsonb)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
DECLARE
  pid uuid;
  n int;
BEGIN
  SELECT d.profile_id INTO pid FROM clinical.documents d
    WHERE d.id = p_document_id AND d.deleted_at IS NULL;
  IF NOT FOUND THEN RETURN 'unknown'; END IF;
  INSERT INTO clinical.extraction_runs (id, profile_id, document_id, pipeline_version, model,
      prompt_version, raw_output, confidence, cost_usd, status)
    VALUES (p_run_id, pid, p_document_id, p_pipeline_version, p_model, p_prompt_version,
      p_raw_output, p_confidence, p_cost_usd, 'completed')
    ON CONFLICT (id) DO NOTHING;
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n = 0 THEN RETURN 'duplicate'; END IF;
  INSERT INTO clinical.extraction_fields (profile_id, run_id, field_path, value, confidence,
      source_page, source_box)
    SELECT pid, p_run_id, f.field_path, f.value, f.confidence, f.source_page, f.source_box
    FROM jsonb_to_recordset(p_fields) AS f(field_path text, value text, confidence real,
      source_page int, source_box jsonb);
  RETURN 'ingested';
END $$"""

_DEFINER = "extraction_ingest_definer"


def _create_role(name: str) -> None:
    op.execute(
        f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{name}') "
        f"THEN CREATE ROLE {name} NOLOGIN; END IF; END $$"
    )


def upgrade() -> None:
    _create_role(_DEFINER)
    _create_role("api_events_consumer")
    for stmt in (
        f"GRANT USAGE ON SCHEMA clinical TO {_DEFINER}, api_events_consumer",
        f"GRANT SELECT (id, profile_id, deleted_at) ON clinical.documents TO {_DEFINER}",
        f"GRANT INSERT (id, profile_id, document_id, pipeline_version, model, prompt_version, "
        f"raw_output, confidence, cost_usd, status) ON clinical.extraction_runs TO {_DEFINER}",
        f"GRANT INSERT (profile_id, run_id, field_path, value, confidence, source_page, "
        f"source_box) ON clinical.extraction_fields TO {_DEFINER}",
        f"GRANT SELECT (id) ON clinical.extraction_runs TO {_DEFINER}",  # ON CONFLICT (id)
        f"CREATE POLICY ingest_definer_select ON clinical.documents FOR SELECT TO {_DEFINER} "
        "USING (true)",
        # no FOR clause: ON CONFLICT also evaluates SELECT policies; column grants cap it
        f"CREATE POLICY ingest_definer_insert ON clinical.extraction_runs TO {_DEFINER} "
        "USING (true) WITH CHECK (true)",
        f"CREATE POLICY ingest_definer_insert ON clinical.extraction_fields FOR INSERT "
        f"TO {_DEFINER} WITH CHECK (true)",
        _FUNCTION,
        f"ALTER FUNCTION {_SIG} OWNER TO {_DEFINER}",
        f"REVOKE EXECUTE ON FUNCTION {_SIG} FROM PUBLIC",
        f"GRANT EXECUTE ON FUNCTION {_SIG} TO api_events_consumer",
    ):
        op.execute(stmt)


def downgrade() -> None:
    op.execute(f"DROP FUNCTION {_SIG}")
    op.execute("DROP POLICY ingest_definer_select ON clinical.documents")
    op.execute("DROP POLICY ingest_definer_insert ON clinical.extraction_runs")
    op.execute("DROP POLICY ingest_definer_insert ON clinical.extraction_fields")
    for t in ("documents", "extraction_runs", "extraction_fields"):
        op.execute(f"REVOKE ALL ON clinical.{t} FROM {_DEFINER}")
    op.execute(f"REVOKE USAGE ON SCHEMA clinical FROM {_DEFINER}")
    op.execute(f"DROP ROLE {_DEFINER}")  # api_events_consumer stays: 0004 owns it
