"""data subject rights: hard delete, audit pseudonymisation, erasure receipts (T106, ADR-0006)

- app_rw gets DELETE on the profile-scoped clinical tables (FORCE RLS keeps it to the caller's own
  profiles) and on worker.document_status. It still cannot delete identity rows or touch audit.
- identity.erase_user(user, salt) is a SECURITY DEFINER function owned by NOLOGIN `dsr_definer`:
  deletes the user's identity rows, grants given or received, break-glass grants and outbox events,
  and pseudonymises audit.audit_events.actor_id (legal retention keeps the events, not the person).
- audit.erasure_receipts proves a deletion happened; it holds a hash of the IdP subject only.

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-24
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

_DEFINER = "dsr_definer"
_FN = "identity.erase_user(uuid, text)"
_APP_DELETE = ", ".join(
    f"clinical.{t}"
    for t in (
        "body_findings",
        "conditions",
        "encounters",
        "observations",
        "extraction_fields",
        "extraction_runs",
        "document_pages",
        "documents",
        "share_grants",
    )
)
_FUNCTION = """
CREATE FUNCTION identity.erase_user(p_user uuid, p_salt text) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
DECLARE pids uuid[];
BEGIN
  SELECT coalesce(array_agg(id), '{}') INTO pids
    FROM identity.patient_profiles WHERE owner_user_id = p_user;
  DELETE FROM audit.break_glass_grants WHERE profile_id = ANY (pids);
  DELETE FROM clinical.share_grants WHERE grantee_user_id = p_user OR profile_id = ANY (pids);
  DELETE FROM clinical.outbox WHERE payload ->> 'profile_id' = ANY (pids::text[]);
  DELETE FROM identity.consents WHERE user_id = p_user;
  DELETE FROM identity.patient_profiles WHERE owner_user_id = p_user;
  DELETE FROM identity.users WHERE id = p_user;
  UPDATE audit.audit_events SET actor_id = md5(p_salt || actor_id::text)::uuid
    WHERE actor_id = p_user;
END $$"""
_TABLE = """
CREATE TABLE audit.erasure_receipts (
  id uuid PRIMARY KEY,
  subject_hash text NOT NULL,
  summary jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now()
)"""


def upgrade() -> None:
    op.execute(
        f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{_DEFINER}') "
        f"THEN CREATE ROLE {_DEFINER} NOLOGIN; END IF; END $$"
    )
    op.execute(_TABLE)
    op.execute("CREATE INDEX ON audit.erasure_receipts (subject_hash)")
    for stmt in (
        "GRANT SELECT, INSERT ON audit.erasure_receipts TO app_rw",
        f"GRANT DELETE ON {_APP_DELETE} TO app_rw",
        "GRANT DELETE ON worker.document_status TO app_rw",
        f"GRANT USAGE ON SCHEMA audit, identity, clinical TO {_DEFINER}",
        f"GRANT SELECT, DELETE ON identity.consents, identity.patient_profiles, identity.users "
        f"TO {_DEFINER}",
        f"GRANT SELECT, DELETE ON audit.break_glass_grants, clinical.outbox TO {_DEFINER}",
        f"GRANT SELECT, DELETE ON clinical.share_grants TO {_DEFINER}",
        f"GRANT SELECT, UPDATE (actor_id) ON audit.audit_events TO {_DEFINER}",
        f"CREATE POLICY dsr_definer_all ON clinical.share_grants TO {_DEFINER} USING (true)",
        _FUNCTION,
        f"ALTER FUNCTION {_FN} OWNER TO {_DEFINER}",
        f"REVOKE EXECUTE ON FUNCTION {_FN} FROM PUBLIC",
        f"GRANT EXECUTE ON FUNCTION {_FN} TO app_rw",
    ):
        op.execute(stmt)


def downgrade() -> None:
    op.execute(f"DROP FUNCTION {_FN}")
    op.execute("DROP POLICY dsr_definer_all ON clinical.share_grants")
    op.execute("DROP TABLE audit.erasure_receipts")
    op.execute(f"REVOKE DELETE ON {_APP_DELETE} FROM app_rw")
    op.execute("REVOKE DELETE ON worker.document_status FROM app_rw")
    for rel in (
        "identity.consents, identity.patient_profiles, identity.users",
        "audit.break_glass_grants, clinical.outbox, clinical.share_grants, audit.audit_events",
    ):
        op.execute(f"REVOKE ALL ON {rel} FROM {_DEFINER}")
    op.execute(f"REVOKE USAGE ON SCHEMA audit, identity, clinical FROM {_DEFINER}")
    op.execute(f"DROP ROLE {_DEFINER}")
