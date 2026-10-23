from uuid import UUID

from medilens.modules.extraction.domain.models import (
    ACTION_CONFIRM,
    ACTION_EDIT,
    ExtractionNotFound,
    FieldView,
    ReviewRepository,
    UnconfirmedFields,
)


class ReviewService:
    """The caller commits the DB transaction; the audit row shares it."""

    def __init__(self, repo: ReviewRepository) -> None:
        self._repo = repo

    def _open(self, subject: str, document_id: UUID) -> tuple[UUID, UUID]:
        actor = self._repo.resolve(subject)
        run = self._repo.latest_run(document_id) if actor else None  # RLS hides others' runs
        if actor is None or run is None:
            raise ExtractionNotFound
        return actor, run

    def list_fields(self, subject: str, document_id: UUID) -> list[FieldView]:
        _, run = self._open(subject, document_id)
        return self._repo.fields(run)

    def edit_field(
        self, subject: str, document_id: UUID, field_id: UUID, user_value: str
    ) -> FieldView:
        actor, run = self._open(subject, document_id)
        field = self._repo.set_user_value(run, field_id, user_value)
        if field is None:
            raise ExtractionNotFound
        self._repo.audit(actor, ACTION_EDIT, "extraction_field", field_id)  # ids only, no values
        return field

    def confirm(self, subject: str, document_id: UUID) -> None:
        actor, run = self._open(subject, document_id)
        pending = [
            f.id for f in self._repo.fields(run) if f.needs_confirmation and f.confirmed_at is None
        ]
        if pending:
            raise UnconfirmedFields(pending)
        self._repo.mark_confirmed(run)
        self._repo.audit(actor, ACTION_CONFIRM, "document", document_id)
