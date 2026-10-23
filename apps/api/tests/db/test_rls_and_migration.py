from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from medilens.core.db import make_engine, make_session_factory, scope_to_profiles
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError


def _seed(url: str) -> tuple[UUID, UUID]:
    """Insert two profiles, each with one document, as the owner (bypasses nothing: FORCE RLS
    applies, so we scope per profile)."""
    engine = make_engine(url)
    sessions = make_session_factory(engine)
    ids: list[UUID] = []
    with sessions.begin() as s:
        s.execute(text("SET LOCAL ROLE app_rw"))
        uid = s.execute(
            text("INSERT INTO identity.users (external_sub) VALUES ('sub-1') RETURNING id")
        ).scalar_one()
        for _ in range(2):
            ids.append(
                s.execute(
                    text(
                        "INSERT INTO identity.patient_profiles (owner_user_id) "
                        "VALUES (:u) RETURNING id"
                    ),
                    {"u": uid},
                ).scalar_one()
            )
    for pid in ids:
        with sessions.begin() as s:
            s.execute(text("SET LOCAL ROLE app_rw"))
            scope_to_profiles(s, [pid])
            s.execute(
                text(
                    "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime) "
                    "VALUES (:p, :k, 'x', 'application/pdf')"
                ),
                {"p": pid, "k": f"synthetic/{pid}"},
            )
    engine.dispose()
    return ids[0], ids[1]


def test_upgrade_downgrade_roundtrip(pg_url: str, alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
    engine = make_engine(pg_url)
    with engine.connect() as c:
        tables = {
            r[0]
            for r in c.execute(
                text(
                    "SELECT table_schema||'.'||table_name FROM information_schema.tables "
                    "WHERE table_schema IN ('identity','clinical','audit')"
                )
            )
        }
    assert {
        "identity.users",
        "clinical.documents",
        "audit.audit_events",
        "clinical.outbox",
    } <= tables
    command.downgrade(alembic_cfg, "base")
    with engine.connect() as c:
        left = c.execute(
            text(
                "SELECT count(*) FROM pg_namespace WHERE nspname IN ('identity','clinical','audit')"
            )
        ).scalar_one()
    assert left == 0
    engine.dispose()


def test_no_phi_columns_in_clinical_schema(migrated_url: str) -> None:
    engine = make_engine(migrated_url)
    with engine.connect() as c:
        bad = c.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_schema='clinical' "
                "AND (column_name ~ '(^|_)(name|email|phone)($|_)' "
                "AND column_name NOT IN ('name_vi','name_en','name'))"
            )
        ).all()
        names = (
            c.execute(
                text(
                    "SELECT table_name FROM information_schema.columns WHERE table_schema='clinical' "
                    "AND column_name='name'"
                )
            )
            .scalars()
            .all()
        )
    assert bad == []
    assert names == ["observations"]  # lab test name only
    engine.dispose()


def test_uuid_v7_pk_default(migrated_url: str) -> None:
    engine = make_engine(migrated_url)
    with engine.connect() as c:
        u = c.execute(text("SELECT public.uuid_v7()")).scalar_one()
    assert UUID(str(u)).version == 7
    engine.dispose()


def test_rls_isolates_profiles(migrated_url: str) -> None:
    a, b = _seed(migrated_url)
    engine = make_engine(migrated_url)
    sessions = make_session_factory(engine)

    with sessions.begin() as s:
        s.execute(text("SET LOCAL ROLE app_rw"))
        scope_to_profiles(s, [a])
        rows = s.execute(text("SELECT profile_id FROM clinical.documents")).scalars().all()
        assert [UUID(str(r)) for r in rows] == [a]

    # No scope set -> sees nothing (fail closed).
    with sessions.begin() as s:
        s.execute(text("SET LOCAL ROLE app_rw"))
        assert s.execute(text("SELECT count(*) FROM clinical.documents")).scalar_one() == 0

    # Scope to both -> sees both.
    with sessions.begin() as s:
        s.execute(text("SET LOCAL ROLE app_rw"))
        scope_to_profiles(s, [a, b])
        assert s.execute(text("SELECT count(*) FROM clinical.documents")).scalar_one() == 2

    # Cannot write a row for a profile outside the scope.
    with pytest.raises(DBAPIError), sessions.begin() as s:
        s.execute(text("SET LOCAL ROLE app_rw"))
        scope_to_profiles(s, [a])
        s.execute(
            text(
                "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime) "
                "VALUES (:p, 'k', 'x', 'application/pdf')"
            ),
            {"p": b},
        )
    engine.dispose()


def test_audit_is_append_only_and_partitioned(migrated_url: str) -> None:
    engine = make_engine(migrated_url)
    with engine.connect() as c:
        parts = c.execute(
            text(
                "SELECT count(*) FROM pg_inherits i JOIN pg_class p ON p.oid=i.inhparent "
                "WHERE p.relname='audit_events'"
            )
        ).scalar_one()
        assert parts >= 4  # default + 3 months
        c.execute(text("SET ROLE app_rw"))
        c.execute(text("INSERT INTO audit.audit_events (action) VALUES ('test')"))
        c.commit()
        with pytest.raises(DBAPIError):
            c.execute(text("DELETE FROM audit.audit_events"))
    engine.dispose()


def test_app_ro_cannot_write(migrated_url: str) -> None:
    engine = make_engine(migrated_url)
    with engine.connect() as c:
        c.execute(text("SET ROLE app_ro"))
        with pytest.raises(DBAPIError):
            c.execute(
                text("INSERT INTO identity.users (external_sub) VALUES (:s)"), {"s": str(uuid4())}
            )
    engine.dispose()
