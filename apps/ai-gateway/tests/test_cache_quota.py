from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from medilens_ai_gateway.cache import normalise, similarity
from medilens_ai_gateway.config import load_config
from medilens_ai_gateway.gateway import CompletionRequest, Gateway, GatewayError
from medilens_ai_gateway.main import app
from medilens_ai_gateway.providers import StubProvider
from medilens_ai_gateway.service_token import mint

# All values synthetic.
Q = "Chỉ số HbA1c là gì?"
Q2 = "Creatinine cao nghĩa là gì"


def qa(prompt=Q, profile="p1", **kw):
    return CompletionRequest("t1", profile, prompt, traffic="qa", **kw)


def _cfg(**kw):
    return replace(load_config(), **kw)


def gw(provider=None, **cfg):
    return Gateway(_cfg(**cfg), provider or StubProvider(), wall_clock=lambda: 0)


def test_normalise_and_similarity():
    assert normalise("Chỉ số HbA1c là gì?") == normalise("chi so  hba1c la gi")
    assert similarity(normalise("a b c"), normalise("x y")) == 0.0


def test_paraphrase_hits_and_counts():
    p = StubProvider()
    g = gw(p)
    assert not g.complete(qa()).cached
    r = g.complete(qa("chi so HbA1c la gi ?"))
    assert r.cached and r.cost_usd == 0 and len(p.calls) == 1
    assert (g.qa_cache.hits, g.qa_cache.misses) == (1, 1)


def test_no_cross_profile_or_locale_leak():
    p = StubProvider()
    g = gw(p)
    g.complete(qa())
    assert not g.complete(qa(profile="p2")).cached
    assert not g.complete(qa(locale="en")).cached
    assert len(p.calls) == 3


def test_distinct_question_misses():
    g = gw()
    g.complete(qa())
    assert not g.complete(qa(Q2)).cached


def test_ttl_expiry():
    t = [0.0]
    g = Gateway(load_config(), StubProvider(), clock=lambda: t[0], wall_clock=lambda: 0)
    g.complete(qa())
    t[0] = load_config().cache_ttl_s + 1
    assert not g.complete(qa()).cached


def test_refusals_and_extraction_not_cached():
    g = gw()
    g.complete(qa("bao nhiêu mg"))
    assert g.complete(qa("bao nhiêu mg")).cached is False
    g.complete(CompletionRequest("t1", "p1", "Hemoglobin 13 g/dL"))
    assert len(g.qa_cache._items) == 0


def test_quota_blocks_then_rolls_over_and_cache_is_free():
    now = [1000.0]
    g = Gateway(_cfg(daily_token_quota=10), StubProvider(), wall_clock=lambda: now[0])
    g.complete(qa())  # stub spends > 0 tokens; budget of 10 is reached below
    g.complete(qa(Q2))
    assert g.complete(qa()).cached  # hit: no quota needed even when spent
    with pytest.raises(GatewayError) as e:
        g.complete(qa("Hemoglobin thấp là sao"))
    assert e.value.code == "quota_exceeded" and e.value.retry_after_s == 86_400 - 1000 + 1
    g.complete(qa("Hemoglobin thấp là sao", profile="p2"))  # budget is per user
    now[0] += 86_400
    g.complete(qa("Hemoglobin thấp là sao"))  # new day


SECRET = "test-secret-at-least-32-bytes-long-xxxxxx"


def _auth():
    tok = mint(SECRET, caller="api", tenants=["t"], profiles=["p"], audience="ai-gateway")
    return {"Authorization": f"Bearer {tok}"}


def test_http_traffic_locale_and_429(monkeypatch):
    import medilens_ai_gateway.main as m

    monkeypatch.setenv("AI_GATEWAY_SERVICE_SECRET", SECRET)
    monkeypatch.setattr(m, "_gateway", Gateway(_cfg(daily_token_quota=1), StubProvider()))
    c = TestClient(app)
    body = {"tenant_id": "t", "profile_id": "p", "prompt": "bao nhiêu mg", "traffic": "qa"}
    r = c.post("/v1/complete", json=body, headers=_auth())
    assert r.status_code == 200 and r.json()["guardrail"]["category"] == "dosing"
    body["prompt"] = "HbA1c là gì"
    assert c.post("/v1/complete", json=body, headers=_auth()).json()["cached"] is False
    r = c.post("/v1/complete", json={**body, "prompt": "creatinine là gì"}, headers=_auth())
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0
    r = c.post("/v1/complete", json={**body, "locale": "fr"}, headers=_auth())
    assert r.status_code == 422
