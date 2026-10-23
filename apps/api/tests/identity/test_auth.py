"""Identity authz tests (SEC-ID-04). Local RSA key, no network."""

import time
from typing import Annotated, Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from medilens.core.errors import AppError, app_error_handler
from medilens.modules.identity.api.router import router
from medilens.modules.identity.application.token_validator import TokenValidator, ValidatorConfig
from medilens.modules.identity.infra.jwks import CachedJwks
from medilens.shared import auth as deps

ISS, AUD = "https://idp.test/realms/medilens", "medilens-api"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def jwk(key: Any, kid: str) -> dict[str, Any]:
    d = jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    return {**d, "kid": kid, "use": "sig", "alg": "RS256"}


def token(key: Any = KEY, kid: str = "k1", **over: Any) -> str:
    claims: dict[str, Any] = {
        "sub": "user-1",
        "iss": ISS,
        "aud": AUD,
        "exp": int(time.time()) + 300,
        "realm_access": {"roles": ["patient"]},
    }
    claims.update(over)
    return jwt.encode(
        {k: v for k, v in claims.items() if v is not None}, key, "RS256", {"kid": kid}
    )


@pytest.fixture
def client() -> TestClient:
    doc = {"keys": [jwk(KEY, "k1")]}
    jwks = CachedJwks("https://idp.test/jwks", min_refresh=0, fetch=lambda _u: doc)
    validator = TokenValidator(ValidatorConfig(issuer=ISS, audience=AUD), jwks.get_key)
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(router, prefix="/v1")

    @app.get("/v1/admin-only")
    def admin_only(_: Annotated[Any, Depends(deps.require_role("admin"))]) -> dict[str, str]:
        return {"ok": "yes"}

    app.dependency_overrides[deps.get_token_validator] = lambda: validator
    return TestClient(app)


def bearer(t: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {t}"}


def test_valid_token_returns_principal(client: TestClient) -> None:
    r = client.get("/v1/me", headers=bearer(token()))
    assert r.status_code == 200
    assert r.json() == {"sub": "user-1", "roles": ["patient"]}


def test_cognito_groups_claim(client: TestClient) -> None:
    t = token(realm_access=None, **{"cognito:groups": ["admin"]})
    assert client.get("/v1/admin-only", headers=bearer(t)).status_code == 200


@pytest.mark.parametrize(
    "tok",
    [
        pytest.param(lambda: token(exp=int(time.time()) - 3600), id="expired"),
        pytest.param(lambda: token(aud="other"), id="wrong-audience"),
        pytest.param(lambda: token(iss="https://evil.test"), id="wrong-issuer"),
        pytest.param(lambda: token(key=OTHER), id="bad-signature"),
        pytest.param(lambda: token(kid="unknown"), id="unknown-kid"),
        pytest.param(lambda: "not.a.jwt", id="garbage"),
    ],
)
def test_invalid_token_is_401_problem(client: TestClient, tok: Any) -> None:
    r = client.get("/v1/me", headers=bearer(tok()))
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["status"] == 401


@pytest.mark.parametrize(
    "headers", [{}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer "}]
)
def test_missing_token_is_401(client: TestClient, headers: dict[str, str]) -> None:
    assert client.get("/v1/me", headers=headers).status_code == 401


def test_role_required(client: TestClient) -> None:
    assert client.get("/v1/admin-only", headers=bearer(token())).status_code == 403
    ok = client.get("/v1/admin-only", headers=bearer(token(realm_access={"roles": ["admin"]})))
    assert ok.status_code == 200
    assert client.get("/v1/admin-only").status_code == 401


def test_jwks_rotation_and_cache() -> None:
    docs = [{"keys": [jwk(KEY, "k1")]}, {"keys": [jwk(KEY, "k1"), jwk(OTHER, "k2")]}]
    calls: list[int] = []
    now = [0.0]

    def fetch(_u: str) -> dict[str, Any]:
        calls.append(1)
        return docs[min(len(calls) - 1, 1)]

    j = CachedJwks("https://idp.test/jwks", 3600, 30, fetch=fetch, clock=lambda: now[0])
    j.get_key("k1")
    j.get_key("k1")
    assert len(calls) == 1  # cached
    with pytest.raises(KeyError):
        j.get_key("k2")  # unknown but within min_refresh: no hammering
    assert len(calls) == 1
    now[0] = 60
    assert j.get_key("k2") is not None  # rotated key picked up
    assert len(calls) == 2


def test_me_is_mounted_and_requires_auth() -> None:
    from fastapi.testclient import TestClient
    from medilens.main import create_app

    res = TestClient(create_app()).get("/v1/me")
    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/problem+json")


def test_unregistered_validator_fails_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "_factory", None)
    with pytest.raises(RuntimeError, match="no token validator"):
        deps.get_token_validator()
