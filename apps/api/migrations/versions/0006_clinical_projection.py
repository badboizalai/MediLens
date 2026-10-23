"""clinical projection: provenance (source_run_id) and a display label

source_run_id ties projected rows to the extraction run so a re-confirm replaces them instead of
duplicating. `label` is the plain-language name shown by the viewers (no ICD-10 codes: LIC-002).

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-24
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

_TABLES = ("encounters", "conditions", "observations")


def upgrade() -> None:
    for t in _TABLES:
        op.execute(f"ALTER TABLE clinical.{t} ADD COLUMN source_run_id uuid")
        op.execute(f"CREATE INDEX ON clinical.{t} (source_run_id)")
    op.execute("ALTER TABLE clinical.conditions ADD COLUMN label text")


def downgrade() -> None:
    op.execute("ALTER TABLE clinical.conditions DROP COLUMN label")
    for t in _TABLES:
        op.execute(f"ALTER TABLE clinical.{t} DROP COLUMN source_run_id")
