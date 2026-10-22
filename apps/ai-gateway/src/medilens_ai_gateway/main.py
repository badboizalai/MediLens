from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import load_config
from .gateway import CompletionRequest, Gateway, GatewayError
from .providers import StubProvider

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


_STATUS = {
    "model_not_allowed": 403,
    "scope_required": 422,
    "redaction_failed": 422,
    "provider_timeout": 504,
    "provider_error": 502,
}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/complete")
def complete(body: CompleteBody) -> dict[str, object]:
    try:
        r = get_gateway().complete(CompletionRequest(**body.model_dump()))
    except GatewayError as e:
        raise HTTPException(_STATUS.get(e.code, 500), detail=e.code) from e
    return dict(r.__dict__)
