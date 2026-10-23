from typing import Any
from uuid import uuid4

from .conftest import CARDIOLOGY, ONCOLOGY, Env

PATHS = {"primary.size_mm": "22.5", "metastases[0].site": "liver"}


def findings(env: Env, qs: str = "") -> dict[str, Any]:
    r = env.client.get(f"/v1/profiles/{env.alice_profile}/findings{qs}")
    assert r.status_code == 200, r.text
    return r.json()  # type: ignore[no-any-return]


def test_confirm_projects_and_lists(env: Env) -> None:
    env.run(ONCOLOGY, PATHS)
    assert env.confirm() == 204
    got = {f["region_code"]: f for f in findings(env)["findings"]}
    assert set(got) == {"lung_left_upper", "liver"}  # bone has region null: no finding
    assert got["liver"]["is_metastasis"] is True
    assert got["lung_left_upper"]["is_metastasis"] is False
    assert got["lung_left_upper"]["laterality"] == "left"
    assert got["liver"]["document_id"] == str(env.doc)
    assert got["liver"]["label"] == "metastasis: liver" and got["liver"]["unit_code"] == "oncology"
    assert env.query("SELECT count(*) FROM clinical.conditions") == [(3,)]  # bone kept
    assert env.query("SELECT DISTINCT icd10_code FROM clinical.conditions") == [(None,)]


def test_user_edit_wins(env: Env) -> None:
    env.run(ONCOLOGY, PATHS)
    fid = env.query(
        "SELECT id FROM clinical.extraction_fields WHERE field_path = 'primary.size_mm'"
    )[0][0]
    r = env.client.patch(f"/v1/documents/{env.doc}/fields/{fid}", json={"user_value": "31"})
    assert r.status_code == 200
    assert env.confirm() == 204
    sql = "SELECT size_mm FROM clinical.body_findings WHERE region_code = 'lung_left_upper'"
    assert env.query(sql) == [(31,)]


def test_confirm_twice_does_not_duplicate(env: Env) -> None:
    env.run(CARDIOLOGY)
    assert env.confirm() == 204 and env.confirm() == 204
    body = findings(env)
    assert len(body["findings"]) == 1 and len(body["observations"]) == 1
    for t in ("encounters", "conditions", "body_findings", "observations"):
        sql = f"SELECT count(*) FROM clinical.{t} WHERE deleted_at IS NULL"  # noqa: S608
        assert env.query(sql) == [(1,)]


def test_cursor_pagination(env: Env) -> None:
    env.run(ONCOLOGY, PATHS)
    env.confirm()
    first = findings(env, "?limit=1")
    assert len(first["findings"]) == 1 and first["next_cursor"]
    second = findings(env, f"?limit=1&cursor={first['next_cursor']}")
    assert len(second["findings"]) == 1 and second["next_cursor"] is None
    assert second["findings"][0]["region_code"] != first["findings"][0]["region_code"]
    assert env.client.get(f"/v1/profiles/{env.alice_profile}/findings?limit=101").status_code == 400


def test_other_user_is_404_and_projection_not_triggered(env: Env) -> None:
    env.run(ONCOLOGY, PATHS)
    env.confirm()
    env.current["sub"] = "bob"
    assert env.client.get(f"/v1/profiles/{env.alice_profile}/findings").status_code == 404
    assert env.client.get(f"/v1/profiles/{uuid4()}/findings").status_code == 404
    env.current["sub"] = "stranger"  # no user row at all
    assert env.client.get(f"/v1/profiles/{env.alice_profile}/findings").status_code == 404


def test_unauthenticated_is_401(env: Env) -> None:
    r = env.anon.get(f"/v1/profiles/{env.alice_profile}/findings")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
