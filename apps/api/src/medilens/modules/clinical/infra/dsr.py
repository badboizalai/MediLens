"""Data-subject-rights adapter (T106): export and hard-delete one profile's clinical rows.

Runs as app_rw with the transaction already scoped (RLS) to the owner's profiles. Soft-deleted
rows are included: erasure means gone, not hidden.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

_EXPORT = {
    "encounters": text(
        "SELECT id, date, facility, department_code FROM clinical.encounters "
        "WHERE profile_id = :p ORDER BY id"
    ),
    "conditions": text(
        "SELECT id, label, icd10_code, unit_code, status, severity, stage, onset_date, source "
        "FROM clinical.conditions WHERE profile_id = :p ORDER BY id"
    ),
    "findings": text(
        "SELECT id, condition_id, region_code, laterality, size_mm, severity, is_metastasis, "
        "observed_at FROM clinical.body_findings WHERE profile_id = :p ORDER BY id"
    ),
    "observations": text(
        "SELECT id, loinc_code, name, value, unit, ref_low, ref_high, observed_at "
        "FROM clinical.observations WHERE profile_id = :p ORDER BY id"
    ),
}
# children first: body_findings -> conditions -> encounters
_ERASE = {
    "body_findings": (
        text("DELETE FROM clinical.body_findings WHERE profile_id = :p"),
        text("SELECT 1 FROM clinical.body_findings WHERE profile_id = ANY(:ids) LIMIT 1"),
    ),
    "observations": (
        text("DELETE FROM clinical.observations WHERE profile_id = :p"),
        text("SELECT 1 FROM clinical.observations WHERE profile_id = ANY(:ids) LIMIT 1"),
    ),
    "conditions": (
        text("DELETE FROM clinical.conditions WHERE profile_id = :p"),
        text("SELECT 1 FROM clinical.conditions WHERE profile_id = ANY(:ids) LIMIT 1"),
    ),
    "encounters": (
        text("DELETE FROM clinical.encounters WHERE profile_id = :p"),
        text("SELECT 1 FROM clinical.encounters WHERE profile_id = ANY(:ids) LIMIT 1"),
    ),
}


class SqlClinicalDsr:
    def __init__(self, session: Session) -> None:
        self._s = session

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        return {
            name: [
                dict(r)
                for r in self._s.execute(
                    stmt,
                    {"p": profile_id},
                ).mappings()
            ]
            for name, stmt in _EXPORT.items()
        }

    def erase_profile(self, profile_id: UUID) -> None:
        for delete, _ in _ERASE.values():
            self._s.execute(delete, {"p": profile_id})

    def leftovers(self, profile_ids: list[UUID]) -> list[str]:
        return [
            f"clinical.{t}"
            for t, (_, probe) in _ERASE.items()
            if self._s.execute(probe, {"ids": profile_ids}).first()
        ]
