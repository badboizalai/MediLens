"""Template: confirm an extraction (BR-012, BR-013, BR-035).

Copy the relevant parts into modules/extraction/{api,application,domain,infra}.
"""
# ---------- api/dto.py ----------
from pydantic import BaseModel, ConfigDict, Field


class ConfirmExtractionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=lambda s: "".join(
        w if i == 0 else w.capitalize() for i, w in enumerate(s.split("_"))))
    extraction_id: str
    document_status: str = Field(examples=["confirmed"])
    findings_created: int


# ---------- api/router.py ----------
from fastapi import APIRouter, Depends, Header, status

from medilens.core.security import Principal, current_user
from medilens.modules.extraction.application.services import ExtractionService, get_service

router = APIRouter(prefix="/api/v1/extractions", tags=["extractions"])


@router.post("/{extraction_id}/confirm", response_model=ConfirmExtractionResponse,
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Not found"}, 409: {"description": "Version conflict"},
                        422: {"description": "Unconfirmed fields"}})
async def confirm_extraction(
    extraction_id: str,
    if_match: str = Header(..., alias="If-Match"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    principal: Principal = Depends(current_user),
    service: ExtractionService = Depends(get_service),
) -> ConfirmExtractionResponse:
    result = await service.confirm(principal, extraction_id, etag=if_match, idempotency_key=idempotency_key)
    return ConfirmExtractionResponse(extraction_id=extraction_id,
                                     document_status=result.document_status,
                                     findings_created=result.findings_created)


# ---------- domain/rules.py ----------
class UnconfirmedFields(Exception):
    """Mapped to 422 /errors/unconfirmed-fields."""

    def __init__(self, field_paths: list[str]):
        self.field_paths = field_paths


LOW_CONFIDENCE = 0.7


def ensure_fields_confirmed(fields) -> None:
    """BR-012: fields with confidence < 0.7 must be confirmed by the user."""
    pending = [f.path for f in fields if f.confidence < LOW_CONFIDENCE and f.confirmed_at is None]
    if pending:
        raise UnconfirmedFields(pending)


# ---------- application/services.py ----------
from dataclasses import dataclass


@dataclass
class ConfirmResult:
    document_status: str
    findings_created: int


class ExtractionService:
    def __init__(self, uow, policy, audit, clock):
        self.uow, self.policy, self.audit, self.clock = uow, policy, audit, clock

    async def confirm(self, principal, extraction_id, *, etag: str, idempotency_key: str) -> ConfirmResult:
        async with self.uow.begin(principal=principal) as tx:          # sets app.allowed_profiles for RLS
            cached = await tx.idempotency.get(principal.user_id, idempotency_key)
            if cached:
                return cached
            extraction = await tx.extractions.get_for_update(extraction_id)   # owner-scoped query
            if extraction is None or not await self.policy.can_write(principal, extraction):
                raise NotFound()                                           # 404, never 403
            if extraction.etag != etag:
                raise VersionConflict()
            ensure_fields_confirmed(extraction.fields)                      # BR-012
            extraction.document.transition("confirmed", at=self.clock.now())  # state machine
            tx.outbox.add("ExtractionConfirmed", {"extractionId": extraction.id,
                                                  "documentId": extraction.document.id})
            await self.audit.record(tx, principal, "extraction.confirm", "extraction", extraction.id)  # BR-035
            result = ConfirmResult(document_status="confirmed", findings_created=0)  # findings via materialize job
            await tx.idempotency.save(principal.user_id, idempotency_key, result)
            return result


class NotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


def get_service():  # wired by dependency container
    raise NotImplementedError
