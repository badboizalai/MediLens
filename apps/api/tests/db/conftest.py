from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

API_DIR = Path(__file__).resolve().parents[2]


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    """Superuser URL of a throwaway PostgreSQL 16 (Testcontainers, synthetic data only)."""
    if not _docker_available():
        pytest.skip("Docker not available")
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("pgvector/pgvector:pg16", driver="psycopg") as pg:
        yield pg.get_connection_url()


@pytest.fixture
def alembic_cfg(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Config:
    monkeypatch.setenv("DATABASE_URL", pg_url)
    cfg = Config(str(API_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_DIR / "migrations"))
    return cfg


@pytest.fixture
def migrated_url(pg_url: str, alembic_cfg: Config) -> Iterator[str]:
    command.upgrade(alembic_cfg, "head")
    yield pg_url
    command.downgrade(alembic_cfg, "base")
