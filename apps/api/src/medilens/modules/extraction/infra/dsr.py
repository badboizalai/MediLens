"""Data-subject-rights adapter (T106): export confirmed fields, hard-delete runs and fields."""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

_ERASE = ("extraction_fields", "extraction_runs")  # fields reference runs


class SqlExtractionDsr:
    def __init__(self, session: Session) -> None:
        self._s = session

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        runs = self._s.execute(
            text(
                "SELECT id, document_id, status, model, prompt_version, confidence, created_at "
                "FROM clinical.extraction_runs WHERE profile_id = :p ORDER BY id"
            ),
            {"p": profile_id},
        ).mappings()
        fields = self._s.execute(
            text(
                "SELECT run_id, field_path, value, user_value, confirmed_at "
                "FROM clinical.extraction_fields "
                "WHERE profile_id = :p AND confirmed_at IS NOT NULL ORDER BY id"
            ),
            {"p": profile_id},
        ).mappings()
        by_run: dict[UUID, list[dict[str, Any]]] = {}
        for f in fields:
            by_run.setdefault(f["run_id"], []).append({k: v for k, v in f.items() if k != "run_id"})
        return {
            "extraction_runs": [{**r, "confirmed_fields": by_run.get(r["id"], [])} for r in runs]
        }

    def erase_profile(self, profile_id: UUID) -> None:
        for t in _ERASE:
            self._s.execute(
                text(f"DELETE FROM clinical.{t} WHERE profile_id = :p"),  # noqa: S608
                {"p": profile_id},
            )

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        return [
            f"clinical.{t}"
            for t in _ERASE
            if self._s.execute(
                text(f"SELECT 1 FROM clinical.{t} WHERE profile_id = ANY(:ids) LIMIT 1"),  # noqa: S608
                {"ids": profile_ids},
            ).first()
        ]
