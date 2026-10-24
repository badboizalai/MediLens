"""T106: export, consent withdrawal, erasure. Needs Docker (Testcontainers)."""

from uuid import UUID

from medilens.main import dsr_stores  # noqa: F401
from medilens.modules.identity.domain.dsr import CONFIRM_PHRASE

from tests.dsr.conftest import Env

CONFIRM = {"confirmation": CONFIRM_PHRASE}


def _count(env: Env, sql: str, **p: object) -> int:
    return int(env.query(sql, **p)[0][0])  # type: ignore[call-overload]


def test_export_contains_only_callers_data(env: Env) -> None:
    r = env.client.get("/v1/me/export")
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == str(env.ids["alice"])
    assert {p["id"] for p in body["profiles"]} == {
        str(env.ids["alice_profile"]),
        str(env.ids["alice_gone"]),
    }
    assert {c["type"] for c in body["consents"]} == {"health_data_processing", "research_use"}
    p = next(p for p in body["profiles"] if p["id"] == str(env.ids["alice_profile"]))
    assert p["documents"][0]["original_url"].startswith("https://s3.test/")
    assert "bob" not in r.text
    assert str(env.ids["bob_profile"]) not in r.text


def test_withdraw_sets_withdrawn_at(env: Env) -> None:
    r = env.client.post("/v1/me/consents/research_use/withdraw")
    assert r.status_code == 200 and r.json()["type"] == "research_use"
    rows = env.query(
        "SELECT type, withdrawn_at IS NOT NULL FROM identity.consents WHERE user_id=:u",
        u=env.ids["alice"],
    )
    assert dict(rows) == {"health_data_processing": False, "research_use": True}  # type: ignore[arg-type]
    assert env.client.post("/v1/me/consents/nope/withdraw").status_code == 404


def test_erase_removes_everything_and_keeps_pseudonymised_audit(env: Env) -> None:
    alice, bob_p = env.ids["alice"], env.ids["bob_profile"]
    r = env.client.request("DELETE", "/v1/me", json=CONFIRM)
    assert r.status_code == 200
    receipt = r.json()["receipt_id"]
    assert not [k for k in env.storage.keys if str(env.ids["alice_doc"]) in k]
    assert _count(env, "SELECT count(*) FROM identity.users WHERE id=:u", u=alice) == 0
    assert _count(env, "SELECT count(*) FROM audit.audit_events WHERE actor_id=:u", u=alice) == 0
    assert _count(env, "SELECT count(*) FROM audit.audit_events") >= 2  # retained, pseudonymised
    # the received share is gone, bob's own data untouched
    assert (
        _count(env, "SELECT count(*) FROM clinical.share_grants WHERE grantee_user_id=:u", u=alice)
        == 0
    )
    assert _count(env, "SELECT count(*) FROM clinical.documents WHERE profile_id=:p", p=bob_p) == 1
    assert (
        _count(env, "SELECT count(*) FROM clinical.knowledge_chunks WHERE profile_id=:p", p=bob_p)
        == 1
    )
    assert [k for k in env.storage.keys if str(env.ids["bob_doc"]) in k]
    # idempotent
    again = env.client.request("DELETE", "/v1/me", json=CONFIRM)
    assert again.status_code == 200 and again.json()["receipt_id"] == receipt
    UUID(receipt)


def test_erase_needs_exact_phrase(env: Env) -> None:
    assert env.client.request("DELETE", "/v1/me", json={"confirmation": "yes"}).status_code == 400
    assert _count(env, "SELECT count(*) FROM identity.users WHERE id=:u", u=env.ids["alice"]) == 1


def test_unauthenticated_is_401(env: Env) -> None:
    assert env.anon.get("/v1/me/export").status_code == 401
    assert env.anon.post("/v1/me/consents/research_use/withdraw").status_code == 401
    assert env.anon.request("DELETE", "/v1/me", json=CONFIRM).status_code == 401


def test_unknown_account_is_404(env: Env) -> None:
    env.current["sub"] = "nobody"
    assert env.client.get("/v1/me/export").status_code == 404
    assert env.client.post("/v1/me/consents/research_use/withdraw").status_code == 404
    assert env.client.request("DELETE", "/v1/me", json=CONFIRM).status_code == 404
