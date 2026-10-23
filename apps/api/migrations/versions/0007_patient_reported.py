"""clinical.conditions.source: 'record' (extracted) or 'patient_reported' (BR-040)

Revision ID: 0007_pr
Revises: 0006_admin
Create Date: 2026-10-24
"""

from alembic import op

revision = "0007_pr"
down_revision = "0006_admin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE clinical.conditions ADD COLUMN source text NOT NULL DEFAULT 'record' "
        "CHECK (source IN ('record', 'patient_reported'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE clinical.conditions DROP COLUMN source")
