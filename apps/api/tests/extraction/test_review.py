from typing import Any
from uuid import uuid4

from .conftest import Env


def fields(env: Env) -> dict[str, dict[str, Any]]:
    r = env.client.get(f"/v1/documents/{env.doc}/fields")
    assert r.status_code == 200, r.text
    return {f["field_path"]: f for f in r.json()}


def edit(env: Env, field: Any, value: str = "edited") -> Any:
    return env.client.patch(f"/v1/documents/{env.doc}/fields/{field}", json={"user_value": value})


def test_list_flags_low_confidence(env: Env) -> None:
    f = fields(env)
    assert f["a.low"]["needs_confirmation"] is True
    assert f["b.high"]["needs_confirmation"] is False
    assert f["a.low"]["confirmed_at"] is None and f["a.low"]["source_page"] == 1


def test_edit_sets_user_value_and_audits_ids_only(env: Env) -> None:
    r = edit(env, env.low)
    assert r.status_code == 200 and r.json()["user_value"] == "edited"
    assert r.json()["confirmed_at"] is not None
    rows = env.query("SELECT action, resource_type, resource_id FROM audit.audit_events")
    assert rows == [("extraction.edit_field", "extraction_field", env.low)]


def test_edit_validates_length(env: Env) -> None:
    assert edit(env, env.low, "").status_code == 400
    assert edit(env, env.low, "x" * 2001).status_code == 400


def test_edit_field_not_in_document_is_404(env: Env) -> None:
    assert edit(env, uuid4()).status_code == 404


def test_confirm_blocked_until_low_confidence_confirmed(env: Env) -> None:
    r = env.client.post(f"/v1/documents/{env.doc}/confirm")
    assert r.status_code == 422
    assert r.json()["field_ids"] == [str(env.low)]
    assert r.json()["type"].endswith("/errors/unconfirmed-fields")
    assert env.query("SELECT status FROM clinical.extraction_runs") == [("needs_review",)]

    edit(env, env.low, "ok")
    assert env.client.post(f"/v1/documents/{env.doc}/confirm").status_code == 204
    assert env.query("SELECT status FROM clinical.extraction_runs") == [("confirmed",)]
    assert ("extraction.confirm",) in env.query("SELECT action FROM audit.audit_events")


def test_other_users_document_and_field_are_404(env: Env) -> None:
    env.current["sub"] = "bob"
    assert env.client.get(f"/v1/documents/{env.doc}/fields").status_code == 404
    assert env.client.post(f"/v1/documents/{env.doc}/confirm").status_code == 404
    assert edit(env, env.low).status_code == 404
    assert env.query("SELECT 1 FROM clinical.extraction_fields WHERE user_value IS NOT NULL") == []
    assert env.query("SELECT count(*) FROM audit.audit_events") == [(0,)]


def test_unauthenticated_is_401(env: Env) -> None:
    for method, path in (
        ("get", f"/v1/documents/{env.doc}/fields"),
        ("patch", f"/v1/documents/{env.doc}/fields/{env.low}"),
        ("post", f"/v1/documents/{env.doc}/confirm"),
    ):
        r = getattr(env.anon, method)(path)
        assert r.status_code == 401, (method, r.text)
