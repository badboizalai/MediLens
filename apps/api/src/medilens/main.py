from fastapi import FastAPI

from medilens.core.config import get_settings
from medilens.core.errors import AppError, app_error_handler

settings = get_settings()

app = FastAPI(title="MediLens API", version="0.1.0", docs_url="/docs" if settings.env != "prod" else None)
app.add_exception_handler(AppError, app_error_handler)


@app.get("/healthz", tags=["ops"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Register module routers here as they are implemented:
# from medilens.modules.patient.api.router import router as patient_router
# app.include_router(patient_router, prefix="/v1")
