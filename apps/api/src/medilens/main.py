from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from medilens.core.config import Settings, get_settings
from medilens.core.errors import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from medilens.core.logging import configure_logging
from medilens.core.middleware import RequestIdMiddleware, SecurityHeadersMiddleware
from medilens.modules.admin.api.router import router as admin_router
from medilens.modules.clinical.api.router import router as clinical_router
from medilens.modules.clinical.application.service import ClinicalService
from medilens.modules.clinical.infra.sql_repository import SqlClinicalRepository
from medilens.modules.document.api.router import router as document_router
from medilens.modules.extraction.api import router as extraction_api
from medilens.modules.identity.api.dependencies import get_token_validator
from medilens.modules.identity.api.router import router as identity_router
from medilens.modules.knowledge.api.router import router as knowledge_router
from medilens.shared.auth import register_token_validator

API_PREFIX = "/v1"  # every module router mounts under this prefix


def clinical_confirm_hook(
    session: Annotated[Session, Depends(extraction_api.get_session)],
) -> Callable[[UUID], None]:
    """Confirming an extraction projects it into clinical findings, in the same transaction."""
    return ClinicalService(SqlClinicalRepository(session)).project_run


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.json_logs)
    app = FastAPI(
        title="MediLens API",
        version="0.1.0",
        description="Helps patients understand their records. Illustrates; never diagnoses.",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        openapi_tags=[{"name": "ops", "description": "Liveness and readiness probes"}],
    )
    register_token_validator(
        get_token_validator
    )  # composition root wires identity into shared auth
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "If-Match",
            "Idempotency-Key",
            "X-Request-ID",
        ],
        expose_headers=["X-Request-ID", "ETag"],
    )
    app.add_middleware(SecurityHeadersMiddleware)  # wraps CORS so preflights get headers too
    app.add_middleware(RequestIdMiddleware)  # outermost: ids exist for every response

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"])
    def readyz() -> dict[str, str]:
        # Placeholder: dependency checks (DB, Redis) arrive with their modules.
        return {"status": "ready"}

    v1 = APIRouter(prefix=API_PREFIX)
    # Register module routers here as they are implemented:
    v1.include_router(identity_router)
    v1.include_router(document_router)
    v1.include_router(extraction_api.router)
    v1.include_router(clinical_router)
    v1.include_router(admin_router)
    v1.include_router(knowledge_router)
    # v1.include_router(patient_router)
    app.dependency_overrides[extraction_api.get_confirm_hook] = clinical_confirm_hook
    app.include_router(v1)
    return app


app = create_app()
