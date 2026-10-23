"""Malicious file set through the real upload endpoints (SEC-AP-07, U-02/U-05, AC-02).

The API layer only enforces size + magic bytes + declared==sniffed type. Content-level
controls live downstream; those cases assert the CURRENT API behaviour (accepted, outbox row).
"""

from typing import Any

import pytest
from medilens.modules.document.domain.models import MAX_BYTES

from .conftest import PNG, Env
from .malicious import EICAR, JPEG_ZIP, PDF_HTML, PDF_JS
from .test_upload import outbox, request, upload


def complete(env: Env, data: bytes, declared: str) -> tuple[str, str, Any]:
    doc_id = upload(env, data, declared)
    key = f"quarantine/{env.alice_profile}/{doc_id}"
    return doc_id, key, env.client.post(f"/v1/documents/{doc_id}/complete")


def assert_blocked(env: Env, key: str, r: Any, status: int, kind: str) -> None:
    assert r.status_code == status
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["type"].endswith(kind)
    assert key not in env.storage.objects  # deleted from quarantine
    assert outbox(env) == []  # never published to the worker


@pytest.mark.parametrize("declared", ["application/pdf", "image/jpeg"])
def test_eicar_renamed_is_rejected(env: Env, declared: str) -> None:
    # AC-02: API magic bytes stop it; GuardDuty Malware Protection is the AV layer for real hits.
    _, key, r = complete(env, EICAR, declared)
    assert_blocked(env, key, r, 415, "/unsupported-file-type")


def test_declared_pdf_but_png_bytes_is_rejected(env: Env) -> None:
    _, key, r = complete(env, PNG, "application/pdf")
    assert_blocked(env, key, r, 415, "/unsupported-file-type")


def test_html_without_magic_is_rejected(env: Env) -> None:
    _, key, r = complete(env, b"<html><script>1</script></html>", "application/pdf")
    assert_blocked(env, key, r, 415, "/unsupported-file-type")


def test_empty_object_is_rejected(env: Env) -> None:
    doc_id = request(env, content_type="application/pdf", size_bytes=1).json()["document_id"]
    key = f"quarantine/{env.alice_profile}/{doc_id}"
    env.storage.put(key, b"")  # declared 1 byte at presign, empty on arrival
    r = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert_blocked(env, key, r, 415, "/unsupported-file-type")


def test_empty_declared_size_is_400(env: Env) -> None:
    r = request(env, content_type="application/pdf", size_bytes=0)
    assert r.status_code == 400
    assert r.headers["content-type"].startswith("application/problem+json")
    assert env.query("SELECT count(*) FROM clinical.documents") == [(0,)]


def test_oversize_object_is_413_and_removed(env: Env) -> None:
    doc_id = upload(env, PNG, "image/png")
    key = f"quarantine/{env.alice_profile}/{doc_id}"
    env.storage.sizes[key] = MAX_BYTES + 1  # report size without allocating 20 MB
    r = env.client.post(f"/v1/documents/{doc_id}/complete")
    assert_blocked(env, key, r, 413, "/file-too-large")


@pytest.mark.xfail(
    reason="TODO(S6-T57): API leaves a rejected document 'uploaded-pending'; no 'rejected' status",
    strict=True,
)
def test_rejected_document_status_is_rejected(env: Env) -> None:
    doc_id, _, r = complete(env, EICAR, "application/pdf")
    assert r.status_code == 415
    assert env.client.get(f"/v1/documents/{doc_id}").json()["status"] == "rejected"


@pytest.mark.parametrize(
    ("data", "declared", "downstream"),
    [
        (PDF_JS, "application/pdf", "worker validate: reject /JavaScript, /OpenAction (BUG-05b)"),
        (JPEG_ZIP, "image/jpeg", "worker validate: decode + re-encode drops trailer (BUG-05b)"),
        (PDF_HTML, "application/pdf", "worker validate: strict PDF parse + PDF->image (BUG-05b)"),
    ],
)
def test_content_level_payloads_pass_api_and_are_left_to_worker(
    env: Env, data: bytes, declared: str, downstream: str
) -> None:
    # Valid magic bytes + matching declared type: the API cannot see inside; ``downstream`` blocks.
    _, key, r = complete(env, data, declared)
    assert r.status_code == 200 and r.json()["status"] == "uploaded", downstream
    assert key in env.storage.objects  # stays in quarantine until scan/validate promote it
    assert [row[0] for row in outbox(env)] == ["DocumentUploaded"]
