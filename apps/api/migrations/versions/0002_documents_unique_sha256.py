"""one live document per (profile, sha256): closes the concurrent-upload race

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-23
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Pending rows carry sha256 = '' until completion, so they are excluded.
    op.execute(
        "CREATE UNIQUE INDEX ux_documents_profile_sha256 ON clinical.documents "
        "(profile_id, sha256) WHERE deleted_at IS NULL AND sha256 <> ''"
    )


def downgrade() -> None:
    op.execute("DROP INDEX clinical.ux_documents_profile_sha256")
