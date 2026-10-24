import copy
from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from medilens.modules.clinical.domain.models import (
    EMERGENCY,
    ClinicalRepository,
    FindingView,
    ObservationView,
    ProfileNotFound,
    ReportResult,
    norm,
    project,
)

MAX_LIMIT = 100


class ClinicalService:
    """The caller commits the DB transaction."""

    def __init__(
        self,
        repo: ClinicalRepository,
        locate: Callable[[str], tuple[str | None, str | None]] = lambda _: (None, None),
    ) -> None:
        self._repo = repo
        self._locate = locate

    def report(
        self, subject: str, profile_id: UUID, text: str, observed_at: datetime | None
    ) -> ReportResult:
        """BR-041: emergency signs short-circuit to 115 and nothing is stored (simplest safe
        behaviour: the user acts first; they can re-enter details after). BR-040: no ICD, no
        severity. Unmapped text is kept as a condition without a region. The text is never logged."""
        user = self._repo.resolve(subject)
        if user is None or not self._repo.owns(user, profile_id):
            raise ProfileNotFound
        if EMERGENCY.search(norm(text)):
            return ReportResult(emergency=True)
        region, side = self._locate(text)
        cid = self._repo.add_reported(profile_id, text, region, side, observed_at)
        return ReportResult(False, cid, region, side)

    def project_run(self, run_id: UUID) -> None:
        """Idempotent: replaces whatever an earlier confirm of this run projected."""
        loaded = self._repo.load_run(run_id)
        if loaded is None:
            return
        profile_id, raw, overrides = loaded
        projection = project(copy.deepcopy(raw), overrides)
        if projection is not None:
            self._repo.replace(run_id, profile_id, projection)

    def list_findings(
        self, subject: str, profile_id: UUID, cursor: UUID | None, limit: int
    ) -> tuple[list[FindingView], list[ObservationView], UUID | None]:
        """Observations ride on the first page only; the cursor pages findings."""
        user = self._repo.resolve(subject)
        if user is None or not self._repo.owns(user, profile_id):
            raise ProfileNotFound
        limit = max(1, min(limit, MAX_LIMIT))
        rows = self._repo.findings(profile_id, cursor, limit + 1)
        nxt = rows[limit - 1].id if len(rows) > limit else None
        obs = self._repo.observations(profile_id, MAX_LIMIT) if cursor is None else []
        return rows[:limit], obs, nxt
