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
    """TODO(S5-T43): deskew/crop/quality."""


@job("document.classify", DocStatus.PREPROCESSED, DocStatus.CLASSIFIED)
def classify(ctx: JobContext) -> None:
    """TODO(S5-T43): page classification."""


@job("document.ocr", DocStatus.CLASSIFIED, DocStatus.OCR_DONE)
def ocr(ctx: JobContext) -> None:
    """TODO(S5-T43): OCR body (long step: call ctx.extend_visibility)."""


@job("document.extract", DocStatus.OCR_DONE, DocStatus.EXTRACTED)
def extract(ctx: JobContext) -> None:
    """TODO(S5-T45): LLM structured extraction."""


@job("document.finalize", DocStatus.EXTRACTED, DocStatus.NEEDS_REVIEW)
def finalize(ctx: JobContext) -> None:
    """TODO(S5-T45): materialize results for user review."""
