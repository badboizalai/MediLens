"""PostgreSQL adapter. Run as app_rw; RLS (`app.profile_ids`) is bound per transaction."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from medilens.core.db import scope_to_profiles
from medilens.modules.clinical.domain.models import FindingView, ObservationView, Projection


class SqlClinicalRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def resolve(self, subject: str) -> UUID | None:
        user = self._s.execute(
            text("SELECT id FROM identity.users WHERE external_sub = :s AND deleted_at IS NULL"),
            {"s": subject},
        ).scalar()
        if user is None:
            return None
        ids = self._s.execute(
            text(
                "SELECT id FROM identity.patient_profiles "
                "WHERE owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"u": user},
        ).scalars()
        scope_to_profiles(self._s, list(ids))
        return user

    def owns(self, user_id: UUID, profile_id: UUID) -> bool:
        row = self._s.execute(
            text(
                "SELECT 1 FROM identity.patient_profiles "
                "WHERE id = :p AND owner_user_id = :u AND deleted_at IS NULL"
            ),
            {"p": profile_id, "u": user_id},
        ).first()
        return row is not None

    def load_run(self, run_id: UUID) -> tuple[UUID, dict[str, Any], dict[str, str]] | None:
        run = self._s.execute(
            text(
                "SELECT profile_id, raw_output FROM clinical.extraction_runs "
                "WHERE id = :r AND deleted_at IS NULL"
            ),
            {"r": run_id},
        ).first()
        if run is None or not isinstance(run[1], dict):
            return None
        edits = self._s.execute(
            text(
                "SELECT field_path, user_value FROM clinical.extraction_fields "
                "WHERE run_id = :r AND user_value IS NOT NULL AND deleted_at IS NULL"
            ),
            {"r": run_id},
        )
        return run[0], run[1], {p: v for p, v in edits}

    def _clear(self, run_id: UUID) -> None:
        p = {"r": run_id}
        self._s.execute(
            text(
                "UPDATE clinical.body_findings SET deleted_at = now() "
                "WHERE condition_id IN "
                "(SELECT id FROM clinical.conditions WHERE source_run_id = :r) "
                "AND deleted_at IS NULL"
            ),
            p,
        )
        self._s.execute(
            text(
                "UPDATE clinical.conditions SET deleted_at = now() "
                "WHERE source_run_id = :r AND deleted_at IS NULL"
            ),
            p,
        )
        self._s.execute(
            text(
                "UPDATE clinical.observations SET deleted_at = now() "
                "WHERE source_run_id = :r AND deleted_at IS NULL"
            ),
            p,
        )
        self._s.execute(
            text(
                "UPDATE clinical.encounters SET deleted_at = now() "
                "WHERE source_run_id = :r AND deleted_at IS NULL"
            ),
            p,
        )

    def replace(self, run_id: UUID, profile_id: UUID, pr: Projection) -> None:
        self._clear(run_id)
        enc = self._s.execute(
            text(
                "INSERT INTO clinical.encounters "
                "(profile_id, date, facility, department_code, source_run_id) "
                "VALUES (:p, :d, :f, :dep, :r) RETURNING id"
            ),
            {
                "p": profile_id,
                "d": pr.encounter_date,
                "f": pr.facility,
                "dep": pr.department,
                "r": run_id,
            },
        ).scalar_one()
        for c in pr.conditions:  # icd10_code stays NULL (LIC-002)
            cid = self._s.execute(
                text(
                    "INSERT INTO clinical.conditions (profile_id, encounter_id, unit_code, status, "
                    "severity, stage, label, source_run_id) "
                    "VALUES (:p, :e, :u, :st, :sev, :stage, :l, :r) RETURNING id"
                ),
                {
                    "p": profile_id,
                    "e": enc,
                    "u": c.unit_code,
                    "st": c.status,
                    "sev": c.severity,
                    "stage": c.stage,
                    "l": c.label,
                    "r": run_id,
                },
            ).scalar_one()
            if c.finding:
                f = c.finding
                self._s.execute(
                    text(
                        "INSERT INTO clinical.body_findings (profile_id, condition_id, region_code, "
                        "laterality, size_mm, severity, is_metastasis, observed_at) "
                        "VALUES (:p, :c, :rc, :lat, :size, :sev, :m, CAST(:d AS timestamptz))"
                    ),
                    {
                        "p": profile_id,
                        "c": cid,
                        "rc": f.region_code,
                        "lat": f.laterality,
                        "size": f.size_mm,
                        "sev": c.severity,
                        "m": f.is_metastasis,
                        "d": pr.encounter_date,
                    },
                )
        for o in pr.observations:
            self._s.execute(
                text(
                    "INSERT INTO clinical.observations (profile_id, loinc_code, name, value, unit, "
                    "ref_low, ref_high, observed_at, source_run_id) "
                    "VALUES (:p, :l, :n, :v, :u, :lo, :hi, CAST(:d AS timestamptz), :r)"
                ),
                {
                    "p": profile_id,
                    "l": o.loinc_code,
                    "n": o.name,
                    "v": o.value,
                    "u": o.unit,
                    "lo": o.ref_low,
                    "hi": o.ref_high,
                    "d": pr.encounter_date,
                    "r": run_id,
                },
            )

    def add_reported(
        self,
        profile_id: UUID,
        label: str,
        region_code: str | None,
        laterality: str | None,
        observed_at: datetime | None,
    ) -> UUID:
        """icd10_code and severity stay NULL (BR-040)."""
        cid = self._s.execute(
            text(
                "INSERT INTO clinical.conditions (profile_id, label, source) "
                "VALUES (:p, :l, 'patient_reported') RETURNING id"
            ),
            {"p": profile_id, "l": label},
        ).scalar_one()
        if region_code:
            self._s.execute(
                text(
                    "INSERT INTO clinical.body_findings "
                    "(profile_id, condition_id, region_code, laterality, observed_at) "
                    "VALUES (:p, :c, :rc, :lat, COALESCE(:d, now()))"
                ),
                {"p": profile_id, "c": cid, "rc": region_code, "lat": laterality, "d": observed_at},
            )
        return cid  # type: ignore[no-any-return]

    def findings(self, profile_id: UUID, after: UUID | None, limit: int) -> list[FindingView]:
        rows = self._s.execute(
            text(
                "SELECT bf.id, bf.region_code, bf.laterality, bf.severity, c.unit_code, "
                "bf.is_metastasis, bf.observed_at, r.document_id, c.label, c.source "
                "FROM clinical.body_findings bf "
                "JOIN clinical.conditions c ON c.id = bf.condition_id AND c.deleted_at IS NULL "
                "LEFT JOIN clinical.extraction_runs r ON r.id = c.source_run_id "
                "WHERE bf.profile_id = :p AND bf.deleted_at IS NULL "
                "AND (CAST(:after AS uuid) IS NULL OR bf.id < CAST(:after AS uuid)) "
                "ORDER BY bf.id DESC LIMIT :n"  # uuid_v7: id order is creation order
            ),
            {"p": profile_id, "after": after, "n": limit},
        )
        return [FindingView(*r) for r in rows]

    def observations(self, profile_id: UUID, limit: int) -> list[ObservationView]:
        rows = self._s.execute(
            text(
                "SELECT o.id, o.name, o.value, o.unit, o.loinc_code, o.ref_low, o.ref_high, "
                "o.observed_at, r.document_id FROM clinical.observations o "
                "LEFT JOIN clinical.extraction_runs r ON r.id = o.source_run_id "
                "WHERE o.profile_id = :p AND o.deleted_at IS NULL ORDER BY o.id DESC LIMIT :n"
            ),
            {"p": profile_id, "n": limit},
        )
        return [
            ObservationView(
                r[0],
                r[1],
                r[2],
                r[3],
                r[4],
                None if r[5] is None else float(r[5]),
                None if r[6] is None else float(r[6]),
                r[7],
                r[8],
            )
            for r in rows
        ]
