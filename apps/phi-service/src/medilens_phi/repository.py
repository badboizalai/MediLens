from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class SubjectRecord:
    subject_key: str
    wrapped_data_key: bytes
    fields: dict[str, bytes]  # field name -> ciphertext


class SubjectRepository(Protocol):
    def add(self, record: SubjectRecord) -> None: ...
    def get(self, subject_key: str) -> SubjectRecord | None: ...
    def delete(self, subject_key: str) -> bool: ...


class InMemorySubjectRepository:
    def __init__(self) -> None:
        self._rows: dict[str, SubjectRecord] = {}

    def add(self, record: SubjectRecord) -> None:
        self._rows[record.subject_key] = record

    def get(self, subject_key: str) -> SubjectRecord | None:
        return self._rows.get(subject_key)

    def delete(self, subject_key: str) -> bool:
        return self._rows.pop(subject_key, None) is not None


class SqlSubjectRepository:
    """TODO(S4-T34b): SQLAlchemy implementation on the isolated PHI database."""

    def __init__(self, *_: object, **__: object) -> None:
        raise NotImplementedError("SQL repository pending (S4-T34b)")
