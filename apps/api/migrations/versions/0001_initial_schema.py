"""initial schemas, roles, core tables and row-level security

Revision ID: 0001
Revises:
Create Date: 2026-10-23
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_STD = """
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz"""
_PK = "id uuid PRIMARY KEY DEFAULT public.uuid_v7()"

# Clinical tables carry profile_id (denormalised on children) so one RLS predicate
# applies everywhere. NO name/email/phone columns in the clinical schema.
_TABLES: list[tuple[str, str]] = [
    ("identity.users", "external_sub text NOT NULL UNIQUE, status text NOT NULL DEFAULT 'active'"),
    (
        "identity.patient_profiles",
        "owner_user_id uuid NOT NULL REFERENCES identity.users(id), "
        "birth_year int, sex_at_birth text, is_minor boolean NOT NULL DEFAULT false",
    ),
    (
        "identity.consents",
        "user_id uuid NOT NULL REFERENCES identity.users(id), type text NOT NULL, "
        "terms_version text NOT NULL, given_at timestamptz NOT NULL, withdrawn_at timestamptz",
    ),
    (
        "clinical.documents",
        "profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id), "
        "storage_key text NOT NULL, sha256 text NOT NULL, mime text NOT NULL, "
        "pages int, status text NOT NULL DEFAULT 'uploaded', doc_type text, "
        "uploaded_at timestamptz NOT NULL DEFAULT now()",
    ),
    (
        "clinical.document_pages",
        "profile_id uuid NOT NULL, document_id uuid NOT NULL REFERENCES clinical.documents(id), "
        "page_no int NOT NULL, ocr_text text, ocr_boxes jsonb, quality_score real, "
        "UNIQUE (document_id, page_no)",
    ),
    (
        "clinical.extraction_runs",
        "profile_id uuid NOT NULL, document_id uuid NOT NULL REFERENCES clinical.documents(id), "
        "pipeline_version text, model text, prompt_version text, raw_output jsonb, "
        "confidence real, cost_usd numeric(10,6), status text NOT NULL DEFAULT 'pending'",
    ),
    (
        "clinical.extraction_fields",
        "profile_id uuid NOT NULL, run_id uuid NOT NULL REFERENCES clinical.extraction_runs(id), "
        "field_path text NOT NULL, value text, confidence real, source_page int, "
        "source_box jsonb, user_value text, confirmed_at timestamptz",
    ),
    (
        "clinical.encounters",
        "profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id), "
        "date date, facility text, department_code text",
    ),
    (
        "clinical.conditions",
        "profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id), "
        "encounter_id uuid REFERENCES clinical.encounters(id), icd10_code text, unit_code text, "
        "status text, severity text, stage text, onset_date date",
    ),
    (
        "clinical.body_findings",
        "profile_id uuid NOT NULL, condition_id uuid NOT NULL REFERENCES clinical.conditions(id), "
        "region_code text NOT NULL, laterality text, size_mm numeric(7,2), severity text, "
        "is_metastasis boolean NOT NULL DEFAULT false, observed_at timestamptz",
    ),
    (
        "clinical.observations",
        "profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id), "
        "loinc_code text, name text NOT NULL, value text, unit text, ref_low numeric, "
        "ref_high numeric, observed_at timestamptz",
    ),
    (
        "clinical.share_grants",
        "profile_id uuid NOT NULL REFERENCES identity.patient_profiles(id), "
        "grantee_user_id uuid NOT NULL REFERENCES identity.users(id), scope text NOT NULL, "
        "expires_at timestamptz NOT NULL, revoked_at timestamptz",
    ),
    (
        "clinical.units",
        "code text NOT NULL UNIQUE, name_vi text NOT NULL, name_en text NOT NULL, "
        "parent_code text, mesh_id text, svg_id text, std_code text",
    ),
    (
        "clinical.regions",
        "code text NOT NULL UNIQUE, name_vi text NOT NULL, name_en text NOT NULL, "
        "parent_code text, mesh_id text, svg_id text, std_code text",
    ),
    (
        "clinical.unit_configs",
        "unit_code text NOT NULL REFERENCES clinical.units(code), version int NOT NULL, "
        "config jsonb NOT NULL, published_at timestamptz, UNIQUE (unit_code, version)",
    ),
    (
        "clinical.outbox",
        "event_type text NOT NULL, payload jsonb NOT NULL, published_at timestamptz",
    ),
]

_RLS = [
    "documents", "document_pages", "extraction_runs", "extraction_fields", "encounters",
    "conditions", "body_findings", "observations", "share_grants",
]  # fmt: skip
_PRED = (
    "profile_id = ANY (string_to_array("
    "coalesce(nullif(current_setting('app.profile_ids', true), ''), ''), ',')::uuid[])"
)


def upgrade() -> None:
    for schema in ("identity", "clinical", "audit"):
        op.execute(f"CREATE SCHEMA {schema}")
    for role in ("migrator", "app_rw", "app_ro"):
        op.execute(
            f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{role}') "
            f"THEN CREATE ROLE {role} NOLOGIN; END IF; END $$"
        )
    # UUIDv7 (time-ordered); PostgreSQL 16 has no native generator.
    op.execute(
        """
CREATE OR REPLACE FUNCTION public.uuid_v7() RETURNS uuid LANGUAGE sql VOLATILE AS $$
  SELECT encode(set_bit(set_bit(overlay(uuid_send(gen_random_uuid())
    placing substring(int8send(floor(extract(epoch FROM clock_timestamp()) * 1000)::bigint)
    from 3) from 1 for 6), 52, 1), 53, 1), 'hex')::uuid
$$"""
    )
    op.execute(
        """
CREATE OR REPLACE FUNCTION public.set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END $$"""
    )
    for name, cols in _TABLES:
        op.execute(f"CREATE TABLE {name} ({_PK}, {cols}, {_STD})")
        op.execute(
            f"CREATE TRIGGER trg_updated_at BEFORE UPDATE ON {name} "
            "FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()"
        )
    for t in _RLS:
        op.execute(f"CREATE INDEX ON clinical.{t} (profile_id)")

    # Append-only audit log, partitioned monthly (PK must include the partition key).
    op.execute(
        """
CREATE TABLE audit.audit_events (
  id uuid NOT NULL DEFAULT public.uuid_v7(),
  actor_id uuid, action text NOT NULL, resource_type text, resource_id uuid,
  ip inet, user_agent text,
  at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  PRIMARY KEY (id, at)
) PARTITION BY RANGE (at)"""
    )
    op.execute("CREATE TABLE audit.audit_events_default PARTITION OF audit.audit_events DEFAULT")
    op.execute(
        """
CREATE OR REPLACE FUNCTION audit.ensure_partition(month date) RETURNS void
LANGUAGE plpgsql AS $$
DECLARE m date := date_trunc('month', month)::date;
BEGIN
  EXECUTE format('CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_events '
    'FOR VALUES FROM (%L) TO (%L)', 'audit_events_' || to_char(m, 'YYYY_MM'), m,
    (m + interval '1 month')::date);
END $$"""
    )
    for offset in (0, 1, 2):
        op.execute(
            f"SELECT audit.ensure_partition((current_date + interval '{offset} month')::date)"
        )

    for t in _RLS:
        op.execute(f"ALTER TABLE clinical.{t} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE clinical.{t} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY profile_scope ON clinical.{t} USING ({_PRED}) WITH CHECK ({_PRED})"
        )

    # migrator owns DDL; app_rw is DML-only; app_ro is read-only.
    for stmt in (
        "GRANT USAGE ON SCHEMA identity, clinical, audit TO app_rw, app_ro",
        "GRANT ALL ON SCHEMA identity, clinical, audit TO migrator",
        "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA identity, clinical TO app_rw",
        "GRANT SELECT ON ALL TABLES IN SCHEMA identity, clinical TO app_ro",
        "GRANT SELECT, INSERT ON audit.audit_events TO app_rw",
        "GRANT SELECT ON audit.audit_events TO app_ro",
        # Catalogues are reference data: app_rw may not change them.
        "REVOKE INSERT, UPDATE ON clinical.units, clinical.regions, clinical.unit_configs "
        "FROM app_rw",
    ):
        op.execute(stmt)


def downgrade() -> None:
    for schema in ("audit", "clinical", "identity"):
        op.execute(f"DROP SCHEMA {schema} CASCADE")
    op.execute("DROP FUNCTION public.set_updated_at()")
    op.execute("DROP FUNCTION public.uuid_v7()")
