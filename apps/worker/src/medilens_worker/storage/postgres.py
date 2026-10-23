"""Postgres-backed status + idempotency (schema `worker`, migration 0003)."""

from collections.abc import Iterator, MutableMapping

from sqlalchemy import Engine, create_engine, text

from medilens_worker.pipeline.idempotency import LEASE_SECONDS
from medilens_worker.pipeline.state import DocStatus, guard_transition


class _Reasons(MutableMapping):
    """Write-through `reasons` mapping; only item get/set are used by the runner."""

    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def __setitem__(self, document_id: str, reason: str) -> None:
        with self._e.begin() as c:
            c.execute(
                text("UPDATE worker.document_status SET reason = :r WHERE document_id = :d"),
                {"r": reason, "d": document_id},
            )

    def __getitem__(self, document_id: str) -> str:
        with self._e.connect() as c:
            r = c.execute(
                text("SELECT reason FROM worker.document_status WHERE document_id = :d"),
                {"d": document_id},
            ).scalar()
        if r is None:
            raise KeyError(document_id)
        return r

    def __delitem__(self, document_id: str) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class PgStatusRepo:
    def __init__(self, url: str) -> None:
        self._e = create_engine(url, pool_pre_ping=True)
        self.reasons = _Reasons(self._e)

    def get(self, document_id: str) -> DocStatus:
        with self._e.connect() as c:
            s = c.execute(
                text("SELECT status FROM worker.document_status WHERE document_id = :d"),
                {"d": document_id},
            ).scalar()
        return DocStatus(s) if s else DocStatus.UPLOADED

    def set(self, document_id: str, status: DocStatus) -> None:
        with self._e.begin() as c:  # row lock makes check-then-write atomic across workers
            c.execute(
                text(
                    "INSERT INTO worker.document_status (document_id, status) "
                    "VALUES (:d, 'uploaded') ON CONFLICT (document_id) DO NOTHING"
                ),
                {"d": document_id},
            )
            cur = c.execute(
                text("SELECT status FROM worker.document_status WHERE document_id = :d FOR UPDATE"),
                {"d": document_id},
            ).scalar_one()
            guard_transition(DocStatus(cur), status)
            c.execute(
                text("UPDATE worker.document_status SET status = :s WHERE document_id = :d"),
                {"s": status.value, "d": document_id},
            )


class PgIdempotencyStore:
    def __init__(self, url: str, lease_seconds: float = LEASE_SECONDS) -> None:
        self._e = create_engine(url, pool_pre_ping=True)
        self._lease = lease_seconds

    def claim(self, key: str) -> bool:
        """Atomic lease: insert, or take over an unfinished lease older than the timeout."""
        with self._e.begin() as c:
            res = c.execute(
                text(
                    "INSERT INTO worker.idempotency_keys AS t (key) VALUES (:k) "
                    "ON CONFLICT (key) DO UPDATE SET claimed_at = clock_timestamp() "
                    "WHERE NOT t.done AND t.claimed_at <= clock_timestamp() - make_interval(secs => :l)"
                ),
                {"k": key, "l": self._lease},
            )
        return res.rowcount == 1

    def seen(self, key: str) -> bool:
        with self._e.connect() as c:
            row = c.execute(
                text("SELECT 1 FROM worker.idempotency_keys WHERE key = :k AND done"), {"k": key}
            ).first()
        return row is not None

    def mark(self, key: str) -> None:
        with self._e.begin() as c:
            c.execute(
                text(
                    "INSERT INTO worker.idempotency_keys (key, done) VALUES (:k, true) "
                    "ON CONFLICT (key) DO UPDATE SET done = true"
                ),
                {"k": key},
            )

    def release(self, key: str) -> None:
        with self._e.begin() as c:
            c.execute(
                text("DELETE FROM worker.idempotency_keys WHERE key = :k AND NOT done"), {"k": key}
            )
