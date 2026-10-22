"""<short description>

Revision ID: <rev>
Revises: <down_rev>
Create Date: YYYY-MM-DD

Phase: expand (adds only). Contract step (drops) goes in a later release.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "<rev>"
down_revision = "<down_rev>"


def upgrade() -> None:
    op.create_table(
        "body_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patient_profiles.id"), nullable=False),
        sa.Column("condition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conditions.id"), nullable=False),
        sa.Column("region_code", sa.String(64), nullable=False, comment="C4 PHI: anatomical region or 'unmapped'"),
        sa.Column("laterality", sa.String(16), nullable=False, server_default="unknown"),
        sa.Column("severity", sa.String(16), nullable=True),
        sa.Column("size_mm", sa.Numeric(8, 2), nullable=True),
        sa.Column("is_metastasis", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("observed_at", sa.Date, nullable=True),
        sa.Column("extraction_run_id", postgresql.UUID(as_uuid=True), nullable=False, comment="lineage DAT-02"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_body_findings_profile_observed", "body_findings", ["profile_id", "observed_at"])
    op.execute("ALTER TABLE body_findings ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY owner_or_shared ON body_findings USING ("
        "profile_id = ANY (string_to_array(current_setting('app.allowed_profiles', true), ',')::uuid[]))"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS owner_or_shared ON body_findings")
    op.drop_index("ix_body_findings_profile_observed", table_name="body_findings")
    op.drop_table("body_findings")
