"""narrow SECURITY DEFINER lookup so a grantee can fetch their own share grant (ADR-0006)

clinical.share_grants is FORCE RLS by profile, and a grantee has no scope on the owner's profile.
Instead of widening app.profile_ids, `clinical.get_share_grant(share_id, user_id)` returns only the
grant row whose grantee is that user (expired and revoked rows too: Cedar decides, not SQL). The
API then scopes the request to that single profile after a Cedar permit. Owner NOLOGIN role
`share_lookup_definer` has SELECT on six columns and one policy bound to it alone; EXECUTE goes to
app_rw only.

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-24
"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

_FN = "clinical.get_share_grant(uuid, uuid)"
_FUNCTION = """
CREATE FUNCTION clinical.get_share_grant(p_share_id uuid, p_user_id uuid)
RETURNS TABLE (id uuid, profile_id uuid, grantee_user_id uuid, scope text,
               expires_at timestamptz, revoked_at timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp AS $$
  SELECT g.id, g.profile_id, g.grantee_user_id, g.scope, g.expires_at, g.revoked_at
  FROM clinical.share_grants g
  WHERE g.id = p_share_id AND g.grantee_user_id = p_user_id AND g.deleted_at IS NULL
$$"""


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='share_lookup_definer') "
        "THEN CREATE ROLE share_lookup_definer NOLOGIN; END IF; END $$"
    )
    for stmt in (
        "GRANT USAGE ON SCHEMA clinical TO share_lookup_definer",
        "GRANT SELECT (id, profile_id, grantee_user_id, scope, expires_at, revoked_at, deleted_at) "
        "ON clinical.share_grants TO share_lookup_definer",
        "CREATE POLICY share_lookup ON clinical.share_grants TO share_lookup_definer USING (true)",
        _FUNCTION,
        f"ALTER FUNCTION {_FN} OWNER TO share_lookup_definer",
        f"REVOKE EXECUTE ON FUNCTION {_FN} FROM PUBLIC",
        f"GRANT EXECUTE ON FUNCTION {_FN} TO app_rw",
    ):
        op.execute(stmt)


def downgrade() -> None:
    op.execute(f"DROP FUNCTION {_FN}")
    op.execute("DROP POLICY share_lookup ON clinical.share_grants")
    op.execute("REVOKE ALL ON clinical.share_grants FROM share_lookup_definer")
    op.execute("REVOKE USAGE ON SCHEMA clinical FROM share_lookup_definer")
