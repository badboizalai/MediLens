"""RFC 9457 problem+json errors. Types follow backend-engineer/references/error-catalog.md.

Responses never contain stack traces, SQL or PHI; unexpected errors are generic (SEC-AP-09).
"""

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

PROBLEM_JSON = "application/problem+json"
TYPE_BASE = "https://medilens.app/errors/"
log = structlog.get_logger()


class AppError(Exception):
    status = 400
    code = "MEDILENS-400"
    slug = "bad-request"
    title = "Bad request"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail)
        self.detail = detail


class NotFound(AppError):
    status = 404
    code = "MEDILENS-404"
    slug = "not-found"
    title = "Not found"


class Forbidden(AppError):
    status = 403
    code = "MEDILENS-403"
    slug = "forbidden"
    title = "Forbidden"


def problem(
    request: Request,
    *,
    status: int,
    slug: str,
    title: str,
    detail: str = "",
    errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    rid = getattr(request.state, "request_id", "")
    body: dict[str, object] = {
        "type": TYPE_BASE + slug,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "traceId": rid,
    }
    if errors:
        body["errors"] = errors
    headers = {"X-Request-ID": rid} if rid else None
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON, headers=headers)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return problem(request, status=exc.status, slug=exc.slug, title=exc.title, detail=exc.detail)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Only field path + error type: never echo submitted values (may be PHI).
    errors = [
        {"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "code": e["type"]}
        for e in exc.errors()
    ]
    return problem(
        request,
        status=400,
        slug="validation",
        title="Request validation failed",
        detail="One or more fields are invalid.",
        errors=errors,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error("unhandled_error", error_type=type(exc).__name__)
    return problem(
        request,
        status=500,
        slug="internal",
        title="Internal server error",
        detail="An unexpected error occurred.",
    )
