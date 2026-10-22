"""SQLAlchemy 2 engine/session factory and RLS profile scoping."""

import os
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

_DEFAULT_URL = "postgresql+psycopg://medilens:medilens_dev@localhost:5432/medilens"


def make_engine(url: str | None = None) -> Engine:
    """Engine for the app role. DATABASE_URL is read from the environment."""
    return create_engine(url or os.environ.get("DATABASE_URL", _DEFAULT_URL), pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def scope_to_profiles(session: Session, profile_ids: Iterable[UUID]) -> None:
    """Bind the current transaction to the given profiles (RLS `app.profile_ids`).

    Transaction-local (set_config is_local=true) so pooled connections never leak scope.
    """
    ids = ",".join(str(UUID(str(p))) for p in profile_ids)
    session.execute(text("SELECT set_config('app.profile_ids', :ids, true)"), {"ids": ids})
