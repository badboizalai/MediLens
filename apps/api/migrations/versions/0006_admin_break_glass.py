"""admin break-glass grants and PHI-free admin functions (SEC-AZ-05, ADR-0006 pattern)

audit.break_glass_grants records who may look at which profile until when. Two SECURITY DEFINER
functions owned by the NOLOGIN role `admin_definer` (let through FORCE RLS by one policy for that
role alone; no BYPASSRLS, app.profile_ids never widened):
- audit.admin_stats(): counts only (documents per status, users), no row ever leaves.
- audit.break_glass_documents(grant_id, admin_sub): id/status of ONE profile's documents, only
  while that grant is the caller's, unrevoked and unexpired (checked here with now()).
app_rw gets EXECUTE and may only SELECT/INSERT grants (no UPDATE: a grant cannot be extended).

Revision ID: 0006_admin
Revises: 0005
Create Date: 2026-10-24
"""

from alembic import op

revision = "0006_admin"
down_revision = "0005"
branch_labels = None
depends_on = None

_DEFINER = "admin_definer"
_STATS = "audit.admin_stats()"
_DOCS = "audit.break_glass_documents(uuid, text)"

_TABLE = """
CREATE TABLE audit.break_glass_grants (
  id uuid PRIMARY KEY DEFAULT public.uuid_v7(),
  admin_sub text NOT NULL,
  profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id),
  reason text NOT NULL CHECK (length(btrim(reason)) >= 10),
  ticket text,
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
)"""

_STATS_FN = """
CREATE FUNCTION audit.admin_stats() RETURNS TABLE (metric text, n bigint)
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
  SELECT 'documents.' || d.status, count(*) FROM clinical.documents d
    WHERE d.deleted_at IS NULL GROUP BY d.status
  UNION ALL
  SELECT 'users', count(*) FROM identity.users u WHERE u.deleted_at IS NULL
$$"""

_DOCS_FN = """
CREATE FUNCTION audit.break_glass_documents(p_grant_id uuid, p_admin_sub text)
RETURNS TABLE (id uuid, status text)
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
  SELECT d.id, d.status FROM audit.break_glass_grants g
    JOIN clinical.documents d ON d.profile_id = g.profile_id AND d.deleted_at IS NULL
    WHERE g.id = p_grant_id AND g.admin_sub = p_admin_sub
      AND g.revoked_at IS NULL AND g.expires_at > now()
$$"""


def upgrade() -> None:
    op.execute(
        f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{_DEFINER}') "
        f"THEN CREATE ROLE {_DEFINER} NOLOGIN; END IF; END $$"
    )
    op.execute(_TABLE)
    for stmt in (
        "GRANT SELECT, INSERT ON audit.break_glass_grants TO app_rw",
        f"GRANT USAGE ON SCHEMA audit, identity, clinical TO {_DEFINER}",
        f"GRANT SELECT ON audit.break_glass_grants TO {_DEFINER}",
        f"GRANT SELECT (id, profile_id, status, deleted_at) ON clinical.documents TO {_DEFINER}",
        f"GRANT SELECT (id, deleted_at) ON identity.users TO {_DEFINER}",
        f"CREATE POLICY admin_definer_select ON clinical.documents FOR SELECT TO {_DEFINER} "
        "USING (true)",
        _STATS_FN,
        _DOCS_FN,
        f"ALTER FUNCTION {_STATS} OWNER TO {_DEFINER}",
        f"ALTER FUNCTION {_DOCS} OWNER TO {_DEFINER}",
        f"REVOKE EXECUTE ON FUNCTION {_STATS} FROM PUBLIC",
        f"REVOKE EXECUTE ON FUNCTION {_DOCS} FROM PUBLIC",
        f"GRANT EXECUTE ON FUNCTION {_STATS} TO app_rw",
        f"GRANT EXECUTE ON FUNCTION {_DOCS} TO app_rw",
    ):
        op.execute(stmt)


def downgrade() -> None:
    op.execute(f"DROP FUNCTION {_STATS}")
    op.execute(f"DROP FUNCTION {_DOCS}")
    op.execute("DROP POLICY admin_definer_select ON clinical.documents")
    op.execute("DROP TABLE audit.break_glass_grants")
    op.execute(f"REVOKE ALL ON clinical.documents, identity.users FROM {_DEFINER}")
    op.execute(f"REVOKE USAGE ON SCHEMA audit, identity, clinical FROM {_DEFINER}")
    op.execute(f"DROP ROLE {_DEFINER}")
