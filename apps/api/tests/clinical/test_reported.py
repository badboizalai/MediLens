"""BR-040 / BR-041: patient-reported findings. Synthetic text only."""

from typing import Any
from uuid import uuid4

from medilens.modules.clinical.infra.location_ner import locate

from .conftest import CARDIOLOGY, Env


def report(env: Env, text: str, **kw: Any) -> Any:
    return env.client.post(
        f"/v1/profiles/{env.alice_profile}/reported-findings", json={"text": text, **kw}
    )


def test_ner_maps_side_and_never_guesses() -> None:
    assert locate("đau thận trái") == ("kidney_l", "left")
    assert locate("pain in my right lung") == ("lung_r", "right")
    assert locate("liver ache") == ("liver", None)
    assert locate("đau thận") == (None, None)  # side unknown for a paired organ
    assert locate("đau thận trái và gan") == (None, None)  # two regions
    assert locate("xương") == (None, None)  # group node
    assert locate("mệt mỏi") == (None, None)


def test_reported_has_no_icd_no_severity_and_label(env: Env) -> None:
    r = report(env, "đau thận trái")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["emergency"] is False and body["label_key"] == "you_described"
    assert (body["region_code"], body["laterality"]) == ("kidney_l", "left")
    sql = "SELECT source, icd10_code, severity FROM clinical.conditions"
    assert env.query(sql) == [("patient_reported", None, None)]
    assert env.query("SELECT severity FROM clinical.body_findings") == [(None,)]
    got = env.client.get(f"/v1/profiles/{env.alice_profile}/findings").json()["findings"]
    assert [(f["region_code"], f["source"], f["severity"]) for f in got] == [
        ("kidney_l", "patient_reported", None)
    ]


def test_unmapped_kept_without_region(env: Env) -> None:
    r = report(env, "đau thận")
    assert r.status_code == 201 and "region_code" not in r.json()
    assert r.json()["label_key"] == "you_described"
    assert env.query("SELECT count(*) FROM clinical.conditions") == [(1,)]
    assert env.query("SELECT count(*) FROM clinical.body_findings") == [(0,)]


def test_emergency_first_and_nothing_stored(env: Env) -> None:
    r = report(env, "đau ngực dữ dội bên trái")
    assert r.status_code == 200
    assert r.json() == {"emergency": True, "message_key": "emergency_115"}
    assert env.query("SELECT count(*) FROM clinical.conditions") == [(0,)]


def test_record_findings_are_labelled_record(env: Env) -> None:
    env.run(CARDIOLOGY)
    env.confirm()
    got = env.client.get(f"/v1/profiles/{env.alice_profile}/findings").json()["findings"]
    assert got[0]["source"] == "record"


def test_validation_and_authz(env: Env) -> None:
    assert report(env, "x" * 501).status_code == 400
    assert report(env, "   ").status_code == 400
    url = f"/v1/profiles/{env.alice_profile}/reported-findings"
    assert env.anon.post(url, json={"text": "gan"}).status_code == 401
    env.current["sub"] = "bob"  # cross-user: bob cannot write to alice's profile
    assert env.client.post(url, json={"text": "gan"}).status_code == 404
    other = f"/v1/profiles/{uuid4()}/reported-findings"
    assert env.client.post(other, json={"text": "gan"}).status_code == 404
    assert env.query("SELECT count(*) FROM clinical.conditions") == [(0,)]
