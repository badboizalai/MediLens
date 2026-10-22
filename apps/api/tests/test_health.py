from fastapi.testclient import TestClient
from medilens.core.config import Settings
from medilens.main import app, create_app


def test_healthz() -> None:
    assert TestClient(app).get("/healthz").json() == {"status": "ok"}


def test_readyz() -> None:
    assert TestClient(app).get("/readyz").json() == {"status": "ready"}


def test_openapi_metadata_and_prod_hides_docs() -> None:
    spec = TestClient(app).get("/openapi.json").json()
    assert spec["info"]["title"] == "MediLens API"
    prod = TestClient(create_app(Settings(env="prod")))
    assert prod.get("/docs").status_code == 404
    assert prod.get("/openapi.json").status_code == 404
