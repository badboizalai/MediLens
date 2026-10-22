"""Job handler registry. One handler per pipeline step; bodies are stubs."""

from collections.abc import Callable
from dataclasses import dataclass

from medilens_worker.pipeline.state import DocStatus


@dataclass
class JobContext:
    document_id: str
    attempt: int
    extend_visibility: Callable[[int], None]  # call periodically in long steps


Handler = Callable[[JobContext], None]


@dataclass(frozen=True)
class JobSpec:
    handler: Handler
    src: DocStatus
    dst: DocStatus


REGISTRY: dict[str, JobSpec] = {}


def job(job_type: str, src: DocStatus, dst: DocStatus) -> Callable[[Handler], Handler]:
    def deco(fn: Handler) -> Handler:
        REGISTRY[job_type] = JobSpec(fn, src, dst)
        return fn

    return deco


@job("document.validate", DocStatus.UPLOADED, DocStatus.VALIDATED)
def validate(ctx: JobContext) -> None:
    """TODO(S5-T43): MIME/size/page checks."""


@job("document.preprocess", DocStatus.VALIDATED, DocStatus.PREPROCESSED)
def preprocess(ctx: JobContext) -> None:
    """Quality gate + crop + deskew; a failing page raises RetakeRequired(reason code)."""
    from medilens_worker.ocr import service

    service.run_preprocess(ctx.document_id, service.get_store())


@job("document.classify", DocStatus.PREPROCESSED, DocStatus.CLASSIFIED)
def classify(ctx: JobContext) -> None:
    """TODO(S5-T43): page classification."""


@job("document.ocr", DocStatus.CLASSIFIED, DocStatus.OCR_DONE)
def ocr(ctx: JobContext) -> None:
    """OCR: page text + boxes + quality (long step: extends visibility per page)."""
    from medilens_worker.ocr import service

    service.run_ocr(
        ctx.document_id, service.get_store(), service.get_engine(), ctx.extend_visibility
    )


@job("document.extract", DocStatus.OCR_DONE, DocStatus.EXTRACTED)
def extract(ctx: JobContext) -> None:
    """TODO(S5-T45): LLM structured extraction."""


@job("document.finalize", DocStatus.EXTRACTED, DocStatus.NEEDS_REVIEW)
def finalize(ctx: JobContext) -> None:
    """TODO(S5-T45): materialize results for user review."""
