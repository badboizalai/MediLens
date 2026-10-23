"""worker-owned schema: document processing status and idempotency keys

The worker never touches api tables (ADR-001): no FK to clinical.documents.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-23
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

_STD = """
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()"""
_PK = "id uuid PRIMARY KEY DEFAULT public.uuid_v7()"
_TABLES = {
    "worker.document_status": "document_id text NOT NULL UNIQUE, status text NOT NULL, reason text",
    "worker.idempotency_keys": (
        "key text NOT NULL UNIQUE, claimed_at timestamptz NOT NULL DEFAULT now(), "
        "done boolean NOT NULL DEFAULT false"
    ),
}


def upgrade() -> None:
    op.execute("CREATE SCHEMA worker")
    for name, cols in _TABLES.items():
        op.execute(f"CREATE TABLE {name} ({_PK}, {cols}, {_STD})")
        op.execute(
            f"CREATE TRIGGER trg_updated_at BEFORE UPDATE ON {name} "
            "FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()"
        )
    op.execute("GRANT USAGE ON SCHEMA worker TO app_rw, app_ro")
    op.execute("GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA worker TO app_rw")
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA worker TO app_ro")
    op.execute("GRANT ALL ON SCHEMA worker TO migrator")


def downgrade() -> None:
    op.execute("DROP SCHEMA worker CASCADE")
