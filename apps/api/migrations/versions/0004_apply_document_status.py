"""narrow SECURITY DEFINER function so the api-events consumer can apply document status

The consumer has no profile scope (it serves every profile) and clinical.documents is FORCE RLS.
Rather than widening app.profile_ids or granting BYPASSRLS, the function is owned by a dedicated
NOLOGIN role `doc_status_definer` that is let through RLS by ONE explicit policy bound to that
role alone (TO doc_status_definer). Why a policy and not BYPASSRLS: BYPASSRLS skips every policy
on every table and needs superuser (or rds_superuser) to grant; the policy is scoped to this one
table, and the role's column privileges (SELECT id/status/deleted_at, UPDATE status) cap what it
can do even though the policy itself is permissive. Callers get EXECUTE only, via the NOLOGIN
`api_events_consumer` role (deployment grants it to the consumer's login); no table privileges.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-23
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

# Same order as the Python state machine used to hold (contracts README): forward-only.
_FUNCTION = """
CREATE FUNCTION clinical.apply_document_status(p_document_id uuid, p_status text)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
DECLARE
  pipeline constant text[] := ARRAY['uploaded-pending', 'uploaded', 'validated', 'preprocessed',
    'classified', 'ocr_done', 'extracted', 'needs_review'];
  cur text;
BEGIN
  SELECT d.status INTO cur FROM clinical.documents d
    WHERE d.id = p_document_id AND d.deleted_at IS NULL FOR UPDATE;
  IF NOT FOUND THEN RETURN 'unknown'; END IF;
  -- terminals (incl. API-only rejected/confirmed) are final; confirmed is never set from events
  IF cur <> ALL (pipeline) THEN RETURN 'ignored'; END IF;
  IF p_status IN ('needs_retake', 'failed')
     OR coalesce(array_position(pipeline, p_status), 0) > array_position(pipeline, cur)
  THEN
    UPDATE clinical.documents SET status = p_status WHERE id = p_document_id;
    RETURN 'applied';
  END IF;
  RETURN 'ignored';
END $$"""


def _create_role(name: str) -> None:
    op.execute(
        f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{name}') "
        f"THEN CREATE ROLE {name} NOLOGIN; END IF; END $$"
    )


def upgrade() -> None:
    _create_role("doc_status_definer")
    _create_role("api_events_consumer")
    for stmt in (
        "GRANT USAGE ON SCHEMA clinical TO doc_status_definer, api_events_consumer",
        "GRANT SELECT (id, status, deleted_at), UPDATE (status) "
        "ON clinical.documents TO doc_status_definer",
        "CREATE POLICY status_definer ON clinical.documents TO doc_status_definer "
        "USING (true) WITH CHECK (true)",
        _FUNCTION,
        "ALTER FUNCTION clinical.apply_document_status(uuid, text) OWNER TO doc_status_definer",
        "REVOKE EXECUTE ON FUNCTION clinical.apply_document_status(uuid, text) FROM PUBLIC",
        "GRANT EXECUTE ON FUNCTION clinical.apply_document_status(uuid, text) "
        "TO api_events_consumer",
    ):
        op.execute(stmt)


def downgrade() -> None:
    op.execute("DROP FUNCTION clinical.apply_document_status(uuid, text)")
    op.execute("DROP POLICY status_definer ON clinical.documents")
    op.execute("REVOKE ALL ON clinical.documents FROM doc_status_definer")
    op.execute("REVOKE USAGE ON SCHEMA clinical FROM doc_status_definer, api_events_consumer")
    op.execute("DROP ROLE doc_status_definer")
    op.execute("DROP ROLE api_events_consumer")
