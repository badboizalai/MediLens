import pytest
from fastapi.testclient import TestClient
from medilens.core.config import Settings
from medilens.main import create_app

APP = "https://app.example"


def _client() -> TestClient:
    return TestClient(create_app(Settings(cors_origins=[APP])))


def _preflight(origin: str):
    return _client().options(
        "/v1/documents",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )


def test_preflight_allows_only_app_origin() -> None:
    ok, bad = _preflight(APP), _preflight("https://evil.example")
    assert ok.status_code == 200 and ok.headers["access-control-allow-origin"] == APP
    assert bad.status_code == 400 and "access-control-allow-origin" not in bad.headers


def test_cors_never_wildcard_or_credentialed_by_default() -> None:
    assert _preflight(APP).headers["access-control-allow-origin"] != "*"
    assert "access-control-allow-credentials" not in _preflight(APP).headers


@pytest.mark.parametrize("env", ["local", "dev", "staging", "prod"])
def test_wildcard_rejected_in_every_env(env: str) -> None:
    with pytest.raises(ValueError):
        Settings(env=env, cors_origins=["*"])


def test_security_headers_on_every_response() -> None:
    for r in (_client().get("/healthz"), _client().get("/nope"), _preflight(APP)):
        assert r.headers["x-content-type-options"] == "nosniff"
        assert r.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
        assert r.headers["cache-control"] == "no-store"
        assert "max-age=" in r.headers["strict-transport-security"]
