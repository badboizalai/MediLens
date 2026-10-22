import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from medilens.core.config import Settings
from medilens.core.errors import Forbidden, NotFound
from medilens.main import create_app
from pydantic import BaseModel


class Body(BaseModel):
    full_name: str
    age: int


@pytest.fixture
def client() -> TestClient:
    app: FastAPI = create_app(Settings(env="local"))

    @app.get("/t/notfound")
    def nf() -> None:
        raise NotFound("Record not found.")

    @app.get("/t/forbidden")
    def fb() -> None:
        raise Forbidden()

    @app.post("/t/body")
    def post(b: Body) -> None: ...

    @app.get("/t/boom")
    def boom() -> None:
        raise RuntimeError("SELECT * FROM patients WHERE name='Nguyen Van A'")

    return TestClient(app, raise_server_exceptions=False)


def test_app_error_is_problem_details(client: TestClient) -> None:
    r = client.get("/t/notfound", headers={"X-Request-ID": "req-12345678"})
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json() == {
        "type": "https://medilens.app/errors/not-found",
        "title": "Not found",
        "status": 404,
        "detail": "Record not found.",
        "instance": "/t/notfound",
        "traceId": "req-12345678",
    }


def test_forbidden(client: TestClient) -> None:
    assert client.get("/t/forbidden").status_code == 403


def test_validation_error_lists_fields_without_values(client: TestClient) -> None:
    r = client.post("/t/body", json={"full_name": 5, "age": "Nguyen Van A"})
    assert r.status_code == 400
    body = r.json()
    assert body["type"].endswith("/validation")
    assert {e["field"] for e in body["errors"]} == {"full_name", "age"}
    assert "Nguyen" not in r.text


def test_unhandled_500_is_generic_and_traceable(client: TestClient) -> None:
    r = client.get("/t/boom")
    assert r.status_code == 500
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["type"].endswith("/internal")
    assert r.json()["traceId"] and r.headers["x-request-id"] == r.json()["traceId"]
    for leak in ("SELECT", "Nguyen", "Traceback", "RuntimeError"):
        assert leak not in r.text
