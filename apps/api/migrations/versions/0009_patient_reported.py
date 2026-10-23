"""clinical.conditions.source: 'record' (extracted) or 'patient_reported' (BR-040)

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-24
"""

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE clinical.conditions ADD COLUMN source text NOT NULL DEFAULT 'record' "
        "CHECK (source IN ('record', 'patient_reported'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE clinical.conditions DROP COLUMN source")
