import logging
import os
import time

import pytest
from fastapi.testclient import TestClient
from medilens_phi.crypto import AesGcmEncryptor, DecryptionError
from medilens_phi.main import create_app
from medilens_phi.repository import InMemorySubjectRepository
from medilens_phi.service_token import mint

SECRET = "test-secret"  # noqa: S105


class _Headers(dict):
    """Fresh single-use token on every access (nonces are one-shot)."""

    def __getitem__(self, k):
        return f"Bearer {mint(SECRET, caller='api', audience='phi-service')}"

    def items(self):
        return [("Authorization", self["Authorization"])]

    def keys(self):
        return ["Authorization"]


H = _Headers()
PHI = {
    "display_name": "Nguyen Test Van",
    "birth_date": "1990",
    "phone": "0900000000",
    "email": "synthetic@example.test",
}


@pytest.fixture
def repo():
    return InMemorySubjectRepository()


@pytest.fixture
def client(repo):
    enc = AesGcmEncryptor(os.urandom(32))
    return TestClient(create_app(service_secret=SECRET, encryptor=enc, repo=repo))


def test_encryptor_roundtrip_and_tamper():
    enc = AesGcmEncryptor(os.urandom(32))
    dek = enc.new_data_key()
    blob = enc.encrypt(dek, b"secret", b"ctx")
    assert b"secret" not in blob
    assert enc.decrypt(dek, blob, b"ctx") == b"secret"
    with pytest.raises(DecryptionError):
        enc.decrypt(dek, blob[:-1] + bytes([blob[-1] ^ 1]), b"ctx")
    with pytest.raises(DecryptionError):
        enc.decrypt(dek, blob, b"other-ctx")


def test_create_get_roundtrip_and_stored_encrypted(client, repo):
    key = client.post("/v1/subjects", json=PHI, headers=H).json()["subject_key"]
    assert client.get(f"/v1/subjects/{key}", headers=H).json() == {"subject_key": key, **PHI}
    stored = repo.get(key).fields
    assert all(PHI[k].encode() not in v for k, v in stored.items())


def test_tampered_ciphertext_detected(client, repo):
    key = client.post("/v1/subjects", json=PHI, headers=H).json()["subject_key"]
    rec = repo.get(key)
    b = rec.fields["email"]
    rec.fields["email"] = b[:-1] + bytes([b[-1] ^ 1])
    assert client.get(f"/v1/subjects/{key}", headers=H).status_code == 500


def test_ciphertext_swap_between_fields_detected(client, repo):
    key = client.post("/v1/subjects", json=PHI, headers=H).json()["subject_key"]
    f = repo.get(key).fields
    f["phone"], f["email"] = f["email"], f["phone"]
    assert client.get(f"/v1/subjects/{key}", headers=H).status_code == 500


def _bad_tokens():
    good = mint(SECRET, caller="api", audience="phi-service")
    p, sig = good.split(".")
    other = mint(SECRET, caller="api", audience="ai-gateway")
    return {
        "missing": {},
        "garbage": {"Authorization": "Bearer wrong"},
        "expired": {
            "Authorization": "Bearer "
            + mint(SECRET, caller="api", audience="phi-service", now=time.time() - 600)
        },
        "wrong_audience": {"Authorization": f"Bearer {other}"},
        "tampered": {"Authorization": f"Bearer {p[:-2]}xx.{sig}"},
        "wrong_secret": {
            "Authorization": "Bearer " + mint("other", caller="api", audience="phi-service")
        },
    }


@pytest.mark.parametrize("headers", _bad_tokens().values(), ids=_bad_tokens().keys())
def test_unauthorized(client, headers):
    assert client.post("/v1/subjects", json=PHI, headers=headers).status_code == 401
    assert client.get("/v1/subjects/x", headers=headers).status_code == 401
    assert client.delete("/v1/subjects/x", headers=headers).status_code == 401


def test_no_token_configured_denies_all():
    c = TestClient(create_app(service_secret="", encryptor=AesGcmEncryptor(os.urandom(32))))
    assert c.get("/v1/subjects/x", headers=H).status_code == 401


def test_replayed_token_rejected(client):
    h = {"Authorization": H["Authorization"]}
    assert client.get("/v1/subjects/x", headers=h).status_code == 404
    assert client.get("/v1/subjects/x", headers=h).status_code == 401


def test_ephemeral_kek_refused_outside_local(monkeypatch):
    monkeypatch.delenv("PHI_KEK_B64", raising=False)
    for env in ("prod", "staging", "dev", None):
        if env is None:
            monkeypatch.delenv("ENV", raising=False)
        else:
            monkeypatch.setenv("ENV", env)
        with pytest.raises(RuntimeError, match="PHI_KEK_B64"):
            create_app(service_secret=SECRET)
    monkeypatch.setenv("ENV", "local")
    create_app(service_secret=SECRET)


def test_crypto_shred_makes_data_unreadable(client, repo):
    key = client.post("/v1/subjects", json=PHI, headers=H).json()["subject_key"]
    assert client.delete(f"/v1/subjects/{key}", headers=H).status_code == 204
    assert client.get(f"/v1/subjects/{key}", headers=H).status_code == 404
    assert client.delete(f"/v1/subjects/{key}", headers=H).status_code == 404
    assert repo.get(key) is None  # wrapped data key gone: ciphertext is unrecoverable


def test_no_phi_in_logs(client, caplog):
    caplog.set_level(logging.DEBUG)
    key = client.post("/v1/subjects", json=PHI, headers=H).json()["subject_key"]
    client.get(f"/v1/subjects/{key}", headers=H)
    client.delete(f"/v1/subjects/{key}", headers=H)
    text = caplog.text
    assert "phi.create" in text and "phi.read" in text and "phi.shred" in text
    assert not any(v in text for v in PHI.values())
