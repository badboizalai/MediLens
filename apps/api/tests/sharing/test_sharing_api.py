from uuid import uuid4

from .conftest import Env


def read(env: Env, share_id: str, as_user: str = "bob"):  # type: ignore[no-untyped-def]
    env.current["sub"] = as_user
    return env.client.get(f"/v1/shared/{share_id}/findings")


def test_valid_share_reads_only_the_granted_profile(env: Env) -> None:
    sid = env.share()
    r = read(env, sid)
    assert r.status_code == 200, r.text
    assert [f["region_code"] for f in r.json()["findings"]] == ["liver"]  # not bob's own heart_lv
    assert "document_id" not in r.json()["findings"][0]
    assert ("share.create",) in env.query("SELECT action FROM audit.audit_events")
    assert ("share.use",) in env.query("SELECT action FROM audit.audit_events")


def test_expired_share_is_denied(env: Env) -> None:
    sid = env.share(hours=2)
    env.advance(hours=1, minutes=59)
    assert read(env, sid).status_code == 200
    env.advance(minutes=1)
    r = read(env, sid)
    assert r.status_code == 403
    assert ("share.use_denied",) in env.query("SELECT action FROM audit.audit_events")


def test_revoked_share_is_denied_and_owner_only(env: Env) -> None:
    sid = env.share()
    env.current["sub"] = "bob"
    assert env.client.delete(f"/v1/shares/{sid}").status_code == 404  # grantee cannot revoke
    env.current["sub"] = "carol"
    assert env.client.delete(f"/v1/shares/{sid}").status_code == 404
    env.current["sub"] = "alice"
    assert env.client.delete(f"/v1/shares/{sid}").status_code == 204
    assert env.client.delete(f"/v1/shares/{sid}").status_code == 204  # idempotent
    assert read(env, sid).status_code == 403
    assert ("share.revoke",) in env.query("SELECT action FROM audit.audit_events")


def test_wrong_grantee_is_404(env: Env) -> None:
    sid = env.share()
    assert read(env, sid, "carol").status_code == 404
    assert read(env, sid, "alice").status_code == 404  # even the owner uses the owner API
    assert read(env, str(uuid4())).status_code == 404
    assert read(env, sid, "stranger").status_code == 404


def test_create_is_owner_only_and_validated(env: Env) -> None:
    body = {"grantee_user_id": str(env.users["carol"]), "expires_in_hours": 24}
    env.current["sub"] = "bob"
    assert env.client.post(f"/v1/profiles/{env.profile}/shares", json=body).status_code == 404
    env.current["sub"] = "alice"
    for hours in (0, 169):
        bad = {**body, "expires_in_hours": hours}
        assert env.client.post(f"/v1/profiles/{env.profile}/shares", json=bad).status_code == 400
    ghost = {**body, "grantee_user_id": str(uuid4())}
    assert env.client.post(f"/v1/profiles/{env.profile}/shares", json=ghost).status_code == 404
    assert env.share(hours=168)


def test_list_is_owner_only(env: Env) -> None:
    sid = env.share()
    got = env.client.get(f"/v1/profiles/{env.profile}/shares")
    assert [s["id"] for s in got.json()] == [sid]
    assert got.json()[0]["scope"] == "findings:read"
    env.current["sub"] = "bob"
    assert env.client.get(f"/v1/profiles/{env.profile}/shares").status_code == 404


def test_share_gives_read_only_access(env: Env) -> None:
    sid = env.share()
    env.current["sub"] = "bob"
    for method in (env.client.post, env.client.put, env.client.patch, env.client.delete):
        assert method(f"/v1/shared/{sid}/findings").status_code == 405


def test_unauthenticated_is_401(env: Env) -> None:
    sid = env.share()
    for r in (
        env.anon.get(f"/v1/shared/{sid}/findings"),
        env.anon.post(f"/v1/profiles/{env.profile}/shares", json={}),
        env.anon.get(f"/v1/profiles/{env.profile}/shares"),
        env.anon.delete(f"/v1/shares/{sid}"),
    ):
        assert r.status_code == 401
