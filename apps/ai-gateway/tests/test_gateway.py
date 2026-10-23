import logging
import time

import pytest
from fastapi.testclient import TestClient
from medilens_ai_gateway.config import load_config
from medilens_ai_gateway.gateway import CompletionRequest, Gateway, GatewayError
from medilens_ai_gateway.main import app
from medilens_ai_gateway.providers import StubProvider
from medilens_ai_gateway.redaction import redact
from medilens_ai_gateway.service_token import mint

# All values below are synthetic.
PII_CASES = {
    "phone": ("SĐT 0912 345 678", "0912 345 678"),
    "cccd": ("CCCD 012345678901", "012345678901"),
    "email": ("email nguyen.test@example.vn", "nguyen.test@example.vn"),
    "honorific_vi": ("Bà Trần Thị Mai khám tim", "Trần Thị Mai"),
    "honorific_en": ("Mr. John Smith has a cough", "John Smith"),
    "labelled_name": ("Họ tên: Lê Văn Bình, 40 tuổi", "Lê Văn Bình"),
    "address": ("Địa chỉ: 12 Phố Giả, Quận Thử, Hà Nội", "12 Phố Giả"),
    "address_en": ("lives on street Example Road", "Example Road"),
    "record_no": ("Mã BN: ABC12345 siêu âm", "ABC12345"),
    "mrn": ("MRN 99887766 chest x-ray", "99887766"),
    "dob": ("Ngày sinh: 01/02/1980", "01/02/1980"),
}


@pytest.mark.parametrize("text,secret", PII_CASES.values(), ids=PII_CASES.keys())
def test_redacts_each_pii_class(text, secret):
    out = redact(text)
    assert secret not in out, out


def test_redaction_keeps_clinical_text():
    out = redact("Họ tên: Lê Văn Bình, THA, răng 36")
    assert "THA" in out and "răng 36" in out


@pytest.fixture
def cfg():
    return load_config()


def req(prompt="Bà Trần Thị Mai, SĐT 0912 345 678", **kw):
    return CompletionRequest(tenant_id="t1", profile_id="p1", prompt=prompt, **kw)


def test_provider_never_sees_raw_pii(cfg):
    stub = StubProvider()
    Gateway(cfg, stub).complete(req())
    sent = str(stub.calls[0]["prompt"])
    assert "0912" not in sent and "Trần Thị Mai" not in sent


def test_fail_closed_when_redaction_errors(cfg):
    stub = StubProvider()

    def boom(_: str) -> str:
        raise RuntimeError("redactor down")

    with pytest.raises(GatewayError) as e:
        Gateway(cfg, stub, redactor=boom).complete(req())
    assert e.value.code == "redaction_failed"
    assert stub.calls == []


def test_allowlist_rejects_unknown_model(cfg):
    stub = StubProvider()
    with pytest.raises(GatewayError) as e:
        Gateway(cfg, stub).complete(req(model="gpt-unlisted"))
    assert e.value.code == "model_not_allowed" and stub.calls == []


def test_timeout(cfg):
    from dataclasses import replace

    g = Gateway(replace(cfg, timeout_s=0.05), StubProvider(delay_s=0.3))
    t = time.monotonic()
    with pytest.raises(GatewayError) as e:
        g.complete(req())
    assert e.value.code == "provider_timeout" and time.monotonic() - t < 0.25


def test_metering_uses_config_prices(cfg):
    g = Gateway(cfg, StubProvider())
    r = g.complete(req("hello world"))
    p = cfg.prices[r.model]
    assert r.cost_usd == pytest.approx(
        (r.input_tokens * p.input + r.output_tokens * p.output) / 1e3
    )
    assert g.total_tokens == r.input_tokens + r.output_tokens
    assert g.total_cost_usd == r.cost_usd > 0


def test_cache_hit_same_scope_costs_nothing(cfg):
    stub = StubProvider()
    g = Gateway(cfg, stub)
    g.complete(req("q"))
    r2 = g.complete(req("q"))
    assert r2.cached and r2.cost_usd == 0.0 and len(stub.calls) == 1


def test_cache_scoped_by_tenant_and_profile(cfg):
    stub = StubProvider()
    g = Gateway(cfg, stub)
    g.complete(CompletionRequest("t1", "p1", "q"))
    assert not g.complete(CompletionRequest("t1", "p2", "q")).cached
    assert not g.complete(CompletionRequest("t2", "p1", "q")).cached
    assert len(stub.calls) == 3


def test_scope_required(cfg):
    with pytest.raises(GatewayError) as e:
        Gateway(cfg, StubProvider()).complete(CompletionRequest("", "p", "q"))
    assert e.value.code == "scope_required"


def test_logs_contain_no_raw_pii(cfg, caplog):
    caplog.set_level(logging.DEBUG, logger="medilens.ai_gateway")
    g = Gateway(cfg, StubProvider())
    g.complete(req("Ông Phạm Văn Tèo, CCCD 012345678901, email a.b@example.vn"))
    logs = caplog.text
    assert "completion" in logs
    for secret in ("Phạm Văn Tèo", "012345678901", "a.b@example.vn"):
        assert secret not in logs


SECRET = "test-secret"  # noqa: S105


def _auth(**kw):
    kw.setdefault("tenants", ["t"])
    kw.setdefault("profiles", ["p"])
    kw.setdefault("audience", "ai-gateway")
    tok = mint(kw.pop("secret", SECRET), caller="api", **kw)
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture
def http(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_SERVICE_SECRET", SECRET)
    return TestClient(app)


BODY = {"tenant_id": "t", "profile_id": "p", "prompt": "SĐT 0912 345 678"}


def test_http_endpoint_and_allowlist(http):
    assert http.post("/v1/complete", json=BODY, headers=_auth()).status_code == 200
    r = http.post("/v1/complete", json={**BODY, "model": "nope"}, headers=_auth())
    assert r.status_code == 403


def _bad():
    p, sig = mint(SECRET, caller="api", audience="ai-gateway").split(".")
    return {
        "missing": {},
        "garbage": {"Authorization": "Bearer x"},
        "expired": _auth(now=time.time() - 600),
        "wrong_audience": _auth(audience="phi-service"),
        "tampered": {"Authorization": f"Bearer {p[:-2]}xx.{sig}"},
        "wrong_secret": _auth(secret="other"),
    }


@pytest.mark.parametrize("headers", _bad().values(), ids=_bad().keys())
def test_bad_token_401(http, headers):
    assert http.post("/v1/complete", json=BODY, headers=headers).status_code == 401


def test_secret_unset_fails_closed(monkeypatch):
    monkeypatch.delenv("AI_GATEWAY_SERVICE_SECRET", raising=False)
    r = TestClient(app).post("/v1/complete", json=BODY, headers=_auth())
    assert r.status_code == 401


def test_replayed_token_401(http):
    h = _auth()
    assert http.post("/v1/complete", json=BODY, headers=h).status_code == 200
    assert http.post("/v1/complete", json=BODY, headers=h).status_code == 401


@pytest.mark.parametrize(
    "scope",
    [
        {"tenants": ["other"]},
        {"profiles": ["other"]},
        {"tenants": None},
        {"profiles": None},
    ],
)
def test_scope_escalation_403(http, scope):
    h = _auth(**scope)
    assert http.post("/v1/complete", json=BODY, headers=h).status_code == 403


def test_ttl_over_five_minutes_rejected():
    with pytest.raises(ValueError):
        mint(SECRET, caller="api", audience="ai-gateway", ttl_s=301)
