"""PHI service (level A). Service auth: signed short-lived tokens (docs/architecture/service-auth.md)."""

from __future__ import annotations

import base64
import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from medilens_phi.crypto import AesGcmEncryptor, DecryptionError, Encryptor
from medilens_phi.repository import InMemorySubjectRepository, SubjectRepository
from medilens_phi.service import SubjectNotFound, SubjectService
from medilens_phi.service_token import TokenError, Verifier, bearer

AUDIENCE = "phi-service"

log = logging.getLogger("medilens_phi")


class SubjectIn(BaseModel):
    display_name: str | None = None
    birth_date: str | None = None  # year or ISO date
    phone: str | None = None
    email: str | None = None


class SubjectKey(BaseModel):
    subject_key: str


class SubjectOut(SubjectIn):
    subject_key: str


def create_app(
    *,
    service_secret: str | None = None,
    encryptor: Encryptor | None = None,
    repo: SubjectRepository | None = None,
) -> FastAPI:
    """Unset secret => every protected call is 401. Unset KEK => refused unless ENV=local."""
    secret = (
        service_secret if service_secret is not None else os.environ.get("PHI_SERVICE_SECRET", "")
    )
    verifier = Verifier(secret, AUDIENCE)
    if encryptor is None:
        raw = os.environ.get("PHI_KEK_B64")
        if not raw:
            if os.environ.get("ENV") != "local":
                raise RuntimeError("PHI_KEK_B64 is required unless ENV=local (no ephemeral KEK)")
            log.warning("PHI_KEK_B64 unset: using ephemeral dev key (ENV=local)")
        encryptor = AesGcmEncryptor(base64.b64decode(raw) if raw else os.urandom(32))
    svc = SubjectService(repo or InMemorySubjectRepository(), encryptor)
    app = FastAPI(title="MediLens phi-service")

    def require_service(request: Request) -> None:
        try:
            verifier.verify(bearer(request.headers.get("authorization", "")))
        except TokenError:
            raise HTTPException(
                401, "unauthorized", headers={"WWW-Authenticate": "Bearer"}
            ) from None

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/subjects", status_code=201, dependencies=[Depends(require_service)])
    def create_subject(body: SubjectIn) -> SubjectKey:
        return SubjectKey(subject_key=svc.create(body.model_dump()))

    @app.get("/v1/subjects/{key}", dependencies=[Depends(require_service)])
    def get_subject(key: str) -> SubjectOut:
        try:
            return SubjectOut(subject_key=key, **svc.get(key))
        except SubjectNotFound:
            raise HTTPException(404, "subject not found") from None
        except DecryptionError:
            log.error("integrity failure subject_key=%s", key)
            raise HTTPException(500, "integrity check failed") from None

    @app.delete("/v1/subjects/{key}", status_code=204, dependencies=[Depends(require_service)])
    def delete_subject(key: str) -> None:
        try:
            svc.shred(key)
        except SubjectNotFound:
            raise HTTPException(404, "subject not found") from None

    return app


app = create_app()
