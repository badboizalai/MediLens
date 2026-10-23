"""Job handler registry. One handler per pipeline step; bodies are stubs."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from medilens_worker.pipeline.state import DocStatus


@dataclass
class JobContext:
    document_id: str
    attempt: int
    extend_visibility: Callable[[int], None]  # call periodically in long steps
    message: Mapping[str, object] = field(default_factory=dict)  # parsed job body


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
    """Check the raw upload named by the message and promote it to the worker bucket."""
    from medilens_worker.intake.validate import validate_upload
    from medilens_worker.ocr import service

    validate_upload(ctx.document_id, ctx.message, service.get_store())


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
    """LLM structured extraction via the AI Gateway (S5-T45)."""
    from medilens_worker.extraction.deps import get_deps
    from medilens_worker.extraction.service import run_extraction

    d = get_deps()
    ctx.extend_visibility(300)
    d.save_run(
        run_extraction(
            ctx.document_id, d.load_pages(ctx.document_id), d.client, d.unit_for(ctx.document_id)
        )
    )


@job("document.finalize", DocStatus.EXTRACTED, DocStatus.NEEDS_REVIEW)
def finalize(ctx: JobContext) -> None:
    """Materialize the saved extraction run for user review; the runner then sets NEEDS_REVIEW."""
    from medilens_worker.extraction.deps import get_deps

    d = get_deps()
    run = d.load_run(ctx.document_id)
    if run is None:
        raise LookupError("no_extraction_run")  # retryable: extract may not have committed yet
    d.save_review(run)
