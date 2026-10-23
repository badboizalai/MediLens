import copy
from uuid import UUID

from medilens.modules.clinical.domain.models import (
    ClinicalRepository,
    FindingView,
    ObservationView,
    ProfileNotFound,
    project,
)

MAX_LIMIT = 100


class ClinicalService:
    """The caller commits the DB transaction."""

    def __init__(self, repo: ClinicalRepository) -> None:
        self._repo = repo

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
