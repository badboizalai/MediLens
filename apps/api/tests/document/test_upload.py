import re
from typing import Any
from uuid import uuid4

import pytest
from medilens.modules.document.domain.models import MAX_BYTES, sniff_mime

from .conftest import PDF, PNG, Env


def request(env: Env, profile: Any = None, **body: Any) -> Any:
    payload = {"content_type": "image/png", "size_bytes": len(PNG), **body}
    return env.client.post(f"/v1/profiles/{profile or env.alice_profile}/documents", json=payload)


def upload(env: Env, data: bytes = PNG, content_type: str = "image/png") -> str:
    r = request(env, content_type=content_type, size_bytes=len(data))
    assert r.status_code == 201, r.text
    doc_id = r.json()["document_id"]
    env.storage.put(f"quarantine/{env.alice_profile}/{doc_id}", data)
    return doc_id


def outbox(env: Env) -> list[tuple[Any, ...]]:
    return env.query("SELECT event_type, payload FROM clinical.outbox")


def test_happy_path(env: Env) -> None:
    r = request(env)
    assert r.status_code == 201
    body = r.json()
    doc_id = body["document_id"]
    assert body["method"] == "PUT" and body["headers"] == {"Content-Type": "image/png"}
    assert body["expires_in"] <= 300
    key = f"quarantine/{env.alice_profile}/{doc_id}"
    assert env.storage.presigned[0] == {"key": key, "type": "image/png", "size": len(PNG)}
    assert env.query("SELECT status FROM clinical.documents") == [("uploaded-pending",)]
    assert outbox(env) == []  # nothing published before the upload completes

    env.storage.put(key, PNG)
    done = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert done.status_code == 200 and done.json()["status"] == "uploaded"
    assert env.query("SELECT status, length(sha256) FROM clinical.documents") == [("uploaded", 64)]
    rows = outbox(env)
    assert len(rows) == 1 and rows[0][0] == "DocumentUploaded"
    assert rows[0][1] == {
        "document_id": doc_id,
        "profile_id": str(env.alice_profile),
        "mime": "image/png",
    }


def test_complete_is_idempotent(env: Env) -> None:
    doc_id = upload(env)
    assert env.client.post(f"/v1/documents/{doc_id}/complete").status_code == 200
    assert env.client.post(f"/v1/documents/{doc_id}/complete").status_code == 200
    assert len(outbox(env)) == 1


def test_other_users_profile_is_404_not_403(env: Env) -> None:
    for pid in (env.bob_profile, uuid4()):  # someone else's and a nonexistent profile look alike
        r = request(env, profile=pid)
        assert r.status_code == 404
        assert r.headers["content-type"].startswith("application/problem+json")
    assert env.query("SELECT count(*) FROM clinical.documents") == [(0,)]


def test_idor_on_complete(env: Env) -> None:
    doc_id = upload(env)
    env.as_user("bob")
    missing = env.client.post(f"/v1/documents/{uuid4()}/complete")
    foreign = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json()["detail"] == missing.json()["detail"]
    assert outbox(env) == []


def test_oversize_declared_is_413(env: Env) -> None:
    r = request(env, size_bytes=MAX_BYTES + 1)
    assert r.status_code == 413
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["type"].endswith("/file-too-large")


def test_oversize_actual_is_413_and_object_removed(env: Env) -> None:
    doc_id = upload(env)
    key = f"quarantine/{env.alice_profile}/{doc_id}"
    env.storage.sizes[key] = MAX_BYTES + 1
    r = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert r.status_code == 413
    assert key not in env.storage.objects
    assert outbox(env) == []


def test_unsupported_declared_type(env: Env) -> None:
    r = request(
        env, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert r.status_code == 415
    assert r.json()["type"].endswith("/unsupported-file-type")


def test_polyglot_html_named_pdf_is_rejected(env: Env) -> None:
    html = b"<html><script>alert(1)</script></html>"
    doc_id = upload(env, html, "application/pdf")
    r = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert r.status_code == 415
    assert r.headers["content-type"].startswith("application/problem+json")
    assert env.query("SELECT status FROM clinical.documents") == [("uploaded-pending",)]
    assert outbox(env) == []
    assert env.storage.objects == {}


def test_declared_type_must_match_content(env: Env) -> None:
    doc_id = upload(env, PDF, "image/png")  # real PDF but declared PNG
    assert env.client.post(f"/v1/documents/{doc_id}/complete").status_code == 415


def test_missing_object_is_409(env: Env) -> None:
    doc_id = request(env).json()["document_id"]
    r = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert r.status_code == 409 and r.json()["type"].endswith("/upload-missing")


def test_duplicate_sha256_per_profile(env: Env) -> None:
    first = upload(env)
    assert env.client.post(f"/v1/documents/{first}/complete").status_code == 200
    second = upload(env)
    r = env.client.post(f"/v1/documents/{second}/complete")
    assert r.status_code == 409 and r.json()["type"].endswith("/duplicate-document")
    assert len(outbox(env)) == 1


def test_same_bytes_in_another_profile_is_not_a_duplicate(env: Env) -> None:
    first = upload(env)
    assert env.client.post(f"/v1/documents/{first}/complete").status_code == 200
    env.as_user("bob")
    r = request(env, profile=env.bob_profile)
    doc_id = r.json()["document_id"]
    env.storage.put(f"quarantine/{env.bob_profile}/{doc_id}", PNG)
    assert env.client.post(f"/v1/documents/{doc_id}/complete").status_code == 200


def test_validation_error_is_problem_json(env: Env) -> None:
    r = request(env, size_bytes=0)
    assert r.status_code == 400
    assert r.headers["content-type"].startswith("application/problem+json")


@pytest.mark.parametrize(
    ("head", "mime"),
    [
        (b"\xff\xd8\xff\xe0" + b"x" * 12, "image/jpeg"),
        (PNG, "image/png"),
        (PDF, "application/pdf"),
        (b"\x00\x00\x00\x18ftypheic", "image/heic"),
        (b"\x00\x00\x00\x18ftypmp42", None),
        (b"PK\x03\x04", None),
        (b"<!DOCTYPE html>", None),
    ],
)
def test_sniff_mime(head: bytes, mime: str | None) -> None:
    assert sniff_mime(head) == mime


def test_status_and_outbox_commit_atomically(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    doc_id = upload(env)
    from medilens.shared import outbox as outbox_mod

    def boom(self: Any, *_: Any) -> None:
        raise RuntimeError("db failure")

    monkeypatch.setattr(outbox_mod.SqlOutbox, "add", boom)
    with pytest.raises(RuntimeError):
        env.client.post(f"/v1/documents/{doc_id}/complete")
    # the status update ran before the outbox insert failed: it must have rolled back
    assert env.query("SELECT status FROM clinical.documents") == [("uploaded-pending",)]
    assert outbox(env) == []


def test_unauthenticated_is_401() -> None:
    from fastapi.testclient import TestClient
    from medilens.main import create_app

    r = TestClient(create_app()).post(f"/v1/documents/{uuid4()}/complete")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")


def test_presigned_url_expiry_is_at_most_five_minutes() -> None:
    import boto3
    from botocore.client import Config
    from medilens.modules.document.infra.s3_storage import S3Storage, StorageSettings

    client = boto3.client(
        "s3",
        region_name="ap-southeast-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",  # noqa: S106 - dummy, signing only, no network
        endpoint_url="http://localhost:9000",
        config=Config(signature_version="s3v4"),
    )
    p = S3Storage(StorageSettings(), client).presign_put("quarantine/a/b", "image/png", 10, 300)
    assert int(re.search(r"X-Amz-Expires=(\d+)", p.url).group(1)) <= 300  # type: ignore[union-attr]
    signed = re.search(r"X-Amz-SignedHeaders=([^&]+)", p.url).group(1)  # type: ignore[union-attr]
    assert "content-type" in signed and "content-length" in signed


def test_get_document_owner_other_user_and_unauthenticated(env: Env) -> None:
    doc_id = upload(env)
    ok = env.client.get(f"/v1/documents/{doc_id}")
    assert ok.status_code == 200
    assert ok.json() == {
        "id": doc_id,
        "profile_id": str(env.alice_profile),
        "status": "uploaded-pending",
    }
    env.as_user("bob")
    foreign = env.client.get(f"/v1/documents/{doc_id}")
    missing = env.client.get(f"/v1/documents/{uuid4()}")
    assert foreign.status_code == missing.status_code == 404
    assert foreign.headers["content-type"].startswith("application/problem+json")
    assert foreign.json()["detail"] == missing.json()["detail"]

    from fastapi.testclient import TestClient
    from medilens.main import create_app

    r = TestClient(create_app()).get(f"/v1/documents/{doc_id}")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")


def test_concurrent_duplicate_is_caught_by_unique_index(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from medilens.modules.document.infra.sql_repository import SqlDocumentRepository

    first = upload(env)
    assert env.client.post(f"/v1/documents/{first}/complete").status_code == 200
    second = upload(env)
    # simulate the race: the pre-check saw nothing, the index must still refuse
    monkeypatch.setattr(SqlDocumentRepository, "has_duplicate", lambda *_: False)
    r = env.client.post(f"/v1/documents/{second}/complete")
    assert r.status_code == 409 and r.json()["type"].endswith("/duplicate-document")
    assert len(outbox(env)) == 1
    assert env.query("SELECT count(*) FROM clinical.documents WHERE sha256 <> ''") == [(1,)]


def test_pending_upload_cap_is_429_per_user(env: Env) -> None:
    from medilens.modules.document.domain.models import MAX_PENDING_UPLOADS

    for _ in range(MAX_PENDING_UPLOADS):
        assert request(env).status_code == 201
    r = request(env)
    assert r.status_code == 429
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["type"].endswith("/too-many-pending-uploads")
    env.as_user("bob")  # the cap is per user
    assert request(env, profile=env.bob_profile).status_code == 201


def test_old_pending_uploads_do_not_count_toward_cap(env: Env) -> None:
    from medilens.core.db import make_engine
    from medilens.modules.document.domain.models import MAX_PENDING_UPLOADS
    from sqlalchemy import text

    for _ in range(MAX_PENDING_UPLOADS):
        assert request(env).status_code == 201
    assert request(env).status_code == 429
    engine = make_engine(env.url)
    with engine.begin() as c:  # age every pending row past the window
        c.execute(text("UPDATE clinical.documents SET created_at = now() - interval '1 day'"))
    engine.dispose()
    assert request(env).status_code == 201
