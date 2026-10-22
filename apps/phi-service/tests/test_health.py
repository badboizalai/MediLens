from fastapi.testclient import TestClient
from medilens_phi.main import app


def test_healthz() -> None:
    assert TestClient(app).get("/healthz").json() == {"status": "ok"}
