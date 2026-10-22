import json

import pytest
import structlog
from fastapi.testclient import TestClient
from medilens.core.config import Settings
from medilens.core.logging import configure_logging
from medilens.main import create_app


def test_generates_request_id() -> None:
    r = TestClient(create_app(Settings())).get("/healthz")
    assert len(r.headers["x-request-id"]) == 32


def test_echoes_valid_incoming_id() -> None:
    r = TestClient(create_app(Settings())).get("/healthz", headers={"X-Request-ID": "abc-12345"})
    assert r.headers["x-request-id"] == "abc-12345"


def test_replaces_malformed_incoming_id() -> None:
    r = TestClient(create_app(Settings())).get("/healthz", headers={"X-Request-ID": "bad id!"})
    assert r.headers["x-request-id"] != "bad id!"


def test_cors_from_settings() -> None:
    c = TestClient(create_app(Settings(cors_origins=["https://app.example"])))
    ok = c.get("/healthz", headers={"Origin": "https://app.example"})
    no = c.get("/healthz", headers={"Origin": "https://evil.example"})
    assert ok.headers["access-control-allow-origin"] == "https://app.example"
    assert "access-control-allow-origin" not in no.headers


def test_prod_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError):
        Settings(env="prod", cors_origins=["*"])


def test_logs_are_json_with_request_id_and_no_phi(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", True)
    structlog.contextvars.bind_contextvars(request_id="rid-123456")
    structlog.get_logger().info("x", email="a@b.c", nested={"diagnosis": "d", "ok": 1}, doc_id="42")
    structlog.contextvars.clear_contextvars()
    line = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert line["request_id"] == "rid-123456"
    assert line["email"] == "[REDACTED]"
    assert line["nested"] == {"diagnosis": "[REDACTED]", "ok": 1}
    assert line["doc_id"] == "42"
