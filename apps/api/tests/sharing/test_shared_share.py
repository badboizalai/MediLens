from uuid import uuid4

from .conftest import Env


def get(env: Env, share_id: str, as_user: str = "bob"):  # type: ignore[no-untyped-def]
    env.current["sub"] = as_user
    return env.client.get(f"/v1/shared/{share_id}")


def test_grantee_sees_server_expiry_without_phi(env: Env) -> None:
    sid = env.share(hours=2)
    r = get(env, sid)
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) == {"share_id", "scope", "expires_at", "status"}
    assert body["share_id"] == sid and body["scope"] == "findings:read"
    assert body["status"] == "active"
    assert body["expires_at"].startswith("2026-10-24T14:00:00")  # T0 + 2h
    assert str(env.profile) not in r.text and str(env.users["alice"]) not in r.text


def test_expired_revoked_and_wrong_user_denied(env: Env) -> None:
    sid = env.share(hours=1)
    assert get(env, sid, "carol").status_code == 404
    assert get(env, sid, "alice").status_code == 404
    assert get(env, str(uuid4())).status_code == 404
    env.advance(hours=1)
    assert get(env, sid).status_code == 403
    env.current["sub"] = "alice"
    sid2 = env.share()
    env.current["sub"] = "alice"
    assert env.client.delete(f"/v1/shares/{sid2}").status_code == 204
    assert get(env, sid2).status_code == 403


def test_unauthenticated_is_401(env: Env) -> None:
    assert env.anon.get(f"/v1/shared/{env.share()}").status_code == 401
