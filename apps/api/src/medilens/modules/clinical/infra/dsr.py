"""Data-subject-rights adapter (T106): export and hard-delete one profile's clinical rows.

Runs as app_rw with the transaction already scoped (RLS) to the owner's profiles. Soft-deleted
rows are included: erasure means gone, not hidden.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

_EXPORT = {
    "encounters": "SELECT id, date, facility, department_code FROM clinical.encounters",
    "conditions": (
        "SELECT id, label, icd10_code, unit_code, status, severity, stage, onset_date, source "
        "FROM clinical.conditions"
    ),
    "findings": (
        "SELECT id, condition_id, region_code, laterality, size_mm, severity, is_metastasis, "
        "observed_at FROM clinical.body_findings"
    ),
    "observations": (
        "SELECT id, loinc_code, name, value, unit, ref_low, ref_high, observed_at "
        "FROM clinical.observations"
    ),
}
# children first: body_findings -> conditions -> encounters
_ERASE = ("body_findings", "observations", "conditions", "encounters")


class SqlClinicalDsr:
    def __init__(self, session: Session) -> None:
        self._s = session

    def export_profile(self, profile_id: UUID) -> dict[str, Any]:
        return {
            name: [
                dict(r)
                for r in self._s.execute(
                    text(f"{sql} WHERE profile_id = :p ORDER BY id"),  # noqa: S608
                    {"p": profile_id},
                ).mappings()
            ]
            for name, sql in _EXPORT.items()
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
