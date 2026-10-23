"""Postgres-backed status + idempotency (schema `worker`, migration 0002)."""

from collections.abc import Iterator, MutableMapping

from sqlalchemy import Engine, create_engine, text

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
    def __init__(self, url: str) -> None:
        self._e = create_engine(url, pool_pre_ping=True)

    def seen(self, key: str) -> bool:
        with self._e.connect() as c:
            row = c.execute(
                text("SELECT 1 FROM worker.idempotency_keys WHERE key = :k"), {"k": key}
            ).first()
        return row is not None

    def claim(self, key: str) -> bool:
        """Atomic: True for exactly one caller per key."""
        with self._e.begin() as c:
            res = c.execute(
                text(
                    "INSERT INTO worker.idempotency_keys (key) VALUES (:k) "
                    "ON CONFLICT (key) DO NOTHING"
                ),
                {"k": key},
            )
        return res.rowcount == 1

    def mark(self, key: str) -> None:
        self.claim(key)
