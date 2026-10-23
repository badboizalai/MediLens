from collections.abc import Iterator
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parents[4] / "apps" / "api"


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    """Throwaway PostgreSQL 16 migrated to head with the api migrations (synthetic data only)."""
    if not _docker_available():
        pytest.skip("Docker not available")
    if not list((API_DIR / "migrations/versions").glob("0002_*.py")):
        pytest.skip("api migration 0002 (PR #61) not merged yet")
    from alembic import command
    from alembic.config import Config
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16", driver="psycopg") as pg:
        url = pg.get_connection_url()
        mp = pytest.MonkeyPatch()
        mp.setenv("DATABASE_URL", url)
        cfg = Config(str(API_DIR / "alembic.ini"))
        cfg.set_main_option("script_location", str(API_DIR / "migrations"))
        command.upgrade(cfg, "head")
        command.downgrade(cfg, "0002")  # 0003 must be reversible
        command.upgrade(cfg, "head")
        mp.undo()
        yield url
