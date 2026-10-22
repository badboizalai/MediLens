"""PHI service (level A). Service auth is a shared bearer token: TEMPORARY until mTLS/IAM."""

from __future__ import annotations

import base64
import hmac
import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from medilens_phi.crypto import AesGcmEncryptor, DecryptionError, Encryptor
from medilens_phi.repository import InMemorySubjectRepository, SubjectRepository
from medilens_phi.service import SubjectNotFound, SubjectService

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
    service_token: str | None = None,
    encryptor: Encryptor | None = None,
    repo: SubjectRepository | None = None,
) -> FastAPI:
    """Unset token => every protected call is 401. Unset KEK => ephemeral dev key."""
    token = service_token if service_token is not None else os.environ.get("PHI_SERVICE_TOKEN", "")
    if encryptor is None:
        raw = os.environ.get("PHI_KEK_B64")
        if not raw:
            log.warning("PHI_KEK_B64 unset: using ephemeral dev key")
        encryptor = AesGcmEncryptor(base64.b64decode(raw) if raw else os.urandom(32))
    svc = SubjectService(repo or InMemorySubjectRepository(), encryptor)
    app = FastAPI(title="MediLens phi-service")

    def require_service(request: Request) -> None:
        got = request.headers.get("authorization", "")
        want = f"Bearer {token}"
        if not token or not hmac.compare_digest(got.encode(), want.encode()):
            raise HTTPException(401, "unauthorized", headers={"WWW-Authenticate": "Bearer"})

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
