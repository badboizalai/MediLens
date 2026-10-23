"""knowledge RAG: pgvector chunks of KnowledgeArticles (public) and per-profile record text

profile_id NULL = public article chunk (readable by all, writable only by the ingest/migrator
role); otherwise the row is scoped by the same RLS predicate as the other clinical tables.

Revision ID: 0007
Revises: 0006_admin
Create Date: 2026-10-24
"""

from alembic import op

revision = "0007"
down_revision = "0006_admin"
branch_labels = None
depends_on = None

_PRED = (
    "profile_id = ANY (string_to_array("
    "coalesce(nullif(current_setting('app.profile_ids', true), ''), ''), ',')::uuid[])"
)
DIM = 256  # must match HashingEmbedder.DIM; changing the embedder means a new column + reindex


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        f"""
CREATE TABLE clinical.knowledge_chunks (
  id uuid PRIMARY KEY DEFAULT public.uuid_v7(),
  profile_id uuid REFERENCES identity.patient_profiles(id),
  article_id text,
  language text,
  source_ref text,
  title text,
  content text NOT NULL,
  citations jsonb NOT NULL DEFAULT '[]',
  reviewed boolean NOT NULL DEFAULT false,
  embedding vector({DIM}) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
)"""
    )
    # shortcut: no ANN index; exact scan is fine for ~hundreds of chunks and keeps the profile
    # filter exact. Add hnsw (vector_cosine_ops) when the corpus outgrows it.
    op.execute("CREATE INDEX ON clinical.knowledge_chunks (profile_id)")
    op.execute("CREATE INDEX ON clinical.knowledge_chunks (article_id)")
    op.execute("ALTER TABLE clinical.knowledge_chunks ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE clinical.knowledge_chunks FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY read_scope ON clinical.knowledge_chunks FOR SELECT "
        f"USING (profile_id IS NULL OR {_PRED})"
    )
    op.execute(
        "CREATE POLICY write_scope ON clinical.knowledge_chunks "
        f"USING ({_PRED}) WITH CHECK ({_PRED})"
    )
    op.execute("GRANT SELECT, INSERT, DELETE ON clinical.knowledge_chunks TO app_rw")
    op.execute("GRANT SELECT ON clinical.knowledge_chunks TO app_ro")


def downgrade() -> None:
    op.execute("DROP TABLE clinical.knowledge_chunks")
