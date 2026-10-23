import os
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from .config import load_config
from .gateway import CompletionRequest, Gateway, GatewayError
from .providers import StubProvider
from .service_token import TokenError, Verifier, bearer

AUDIENCE = "ai-gateway"

app = FastAPI(title="MediLens ai-gateway")
_gateway: Gateway | None = None


def get_gateway() -> Gateway:
    global _gateway
    if _gateway is None:
        cfg = load_config()
        if cfg.provider != "stub":
            raise RuntimeError("only the stub provider is implemented in v0")
        _gateway = Gateway(cfg, StubProvider())
    return _gateway


class CompleteBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    prompt: str
    model: str | None = None
    max_output_tokens: int = Field(default=400, ge=1, le=4096)
    tier: Literal["auto"] | None = None
    document_id: str | None = Field(default=None, max_length=128)
    traffic: Literal["qa"] | None = None
    locale: Literal["vi", "en"] = "vi"


_STATUS = {
    "model_not_allowed": 403,
    "scope_required": 422,
    "redaction_failed": 422,
    "provider_timeout": 504,
    "provider_error": 502,
    "quota_exceeded": 429,
}


_verifier: Verifier | None = None


def require_service(request: Request) -> dict[str, Any]:
    """Verify the service token; unset secret => always 401 (fail closed)."""
    global _verifier
    secret = os.environ.get("AI_GATEWAY_SERVICE_SECRET", "")
    if _verifier is None or _verifier.secret != secret:
        _verifier = Verifier(secret, AUDIENCE)
    try:
        return _verifier.verify(bearer(request.headers.get("authorization", "")))
    except TokenError:
        raise HTTPException(401, "unauthorized", headers={"WWW-Authenticate": "Bearer"}) from None


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/complete")
def complete(
    body: CompleteBody,
    claims: Annotated[dict[str, Any], Depends(require_service)],
) -> dict[str, object]:
    # Scope must be inside the token's claims: no caller-supplied escalation.
    tenants, profiles = claims.get("tenants"), claims.get("profiles")
    if not (
        isinstance(tenants, list)
        and isinstance(profiles, list)
        and body.tenant_id in tenants
        and body.profile_id in profiles
    ):
        raise HTTPException(403, "scope_not_permitted")
    try:
        r = get_gateway().complete(CompletionRequest(**body.model_dump()))
    except GatewayError as e:
        headers = {"Retry-After": str(e.retry_after_s)} if e.retry_after_s else None
        raise HTTPException(_STATUS.get(e.code, 500), detail=e.code, headers=headers) from e
    return dict(r.__dict__)
