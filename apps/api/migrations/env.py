import os

from alembic import context
from sqlalchemy import create_engine

config = context.config
url = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://medilens:medilens_dev@localhost:5432/medilens"
)
target_metadata = None  # schema is managed with explicit SQL migrations (RLS, partitions)


def run_migrations_online() -> None:
    # Run as the migrator/owner role, never as app_rw.
    with create_engine(url).connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
