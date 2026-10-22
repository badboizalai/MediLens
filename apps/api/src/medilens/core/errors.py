"""RFC 9457 problem+json errors. Codes follow the catalog in backend-engineer/references/error-catalog.md."""
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status = 400
    code = "MEDILENS-400"

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail)
        self.detail = detail


class NotFound(AppError):
    status = 404
    code = "MEDILENS-404"


class Forbidden(AppError):
    status = 403
    code = "MEDILENS-403"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        media_type="application/problem+json",
        content={"type": f"urn:medilens:error:{exc.code}", "title": exc.code, "status": exc.status, "detail": exc.detail},
    )
