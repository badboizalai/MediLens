import dataclasses

import pytest
from medilens_ai_gateway.config import load_config
from medilens_ai_gateway.gateway import CompletionRequest, Gateway, GatewayError
from medilens_ai_gateway.providers import ProviderResult


class Fake:
    """Returns scripted confidences per model; records (model, prompt)."""

    def __init__(self, conf, valid=True):
        self.conf, self.valid, self.calls = conf, valid, []

    def complete(self, *, model, prompt, max_output_tokens):
        self.calls.append((model, prompt))
        return ProviderResult("{}", 1000, 500, self.conf[model], self.valid)


@pytest.fixture
def cfg():
    return load_config()


def mk(cfg, conf, **kw):
    return Fake({cfg.tier_s_model: conf[0], cfg.tier_m_model: conf[1]}, **kw)


def req(**kw):
    kw.setdefault("prompt", "Bà Trần Thị Mai, SĐT 0912 345 678")
    return CompletionRequest(tenant_id="t1", profile_id="p1", tier="auto", **kw)


def test_threshold_default_is_br012(cfg):
    assert cfg.escalation_threshold == 0.7


def test_high_confidence_stops_at_s(cfg):
    p = mk(cfg, (0.9, 0.9))
    r = Gateway(cfg, p).complete(req())
    assert [m for m, _ in p.calls] == [cfg.tier_s_model]
    assert (r.tier, r.escalated, r.needs_review) == ("S", False, False)


def test_low_s_escalates_once(cfg):
    p = mk(cfg, (0.3, 0.95))
    r = Gateway(cfg, p).complete(req())
    assert [m for m, _ in p.calls] == [cfg.tier_s_model, cfg.tier_m_model]
    assert (r.tier, r.escalated, r.needs_review) == ("M", True, False)


def test_low_m_does_not_loop(cfg):
    p = mk(cfg, (0.1, 0.2))
    r = Gateway(cfg, p).complete(req())
    assert len(p.calls) == 2
    assert (r.tier, r.escalated, r.needs_review) == ("M", True, True)


def test_schema_invalid_escalates(cfg):
    p = mk(cfg, (0.99, 0.99), valid=False)
    r = Gateway(cfg, p).complete(req())
    assert len(p.calls) == 2 and r.needs_review


def test_cache_hit_skips_providers(cfg):
    p = mk(cfg, (0.9, 0.9))
    g = Gateway(cfg, p)
    g.complete(req())
    r = g.complete(req())
    assert len(p.calls) == 1 and r.cached and r.cost_usd == 0.0


def test_cached_escalation_skips_providers(cfg):
    p = mk(cfg, (0.1, 0.9))
    g = Gateway(cfg, p)
    g.complete(req())
    r = g.complete(req())
    assert len(p.calls) == 2 and r.cached and r.escalated


def test_cost_math_and_document_aggregate(cfg):
    p = mk(cfg, (0.1, 0.9))
    g = Gateway(cfg, p)
    r = g.complete(req(document_id="doc-1"))
    s, m = cfg.prices[cfg.tier_s_model], cfg.prices[cfg.tier_m_model]
    want = (1 * s.input + 0.5 * s.output) + (1 * m.input + 0.5 * m.output)
    assert r.cost_usd == pytest.approx(want)
    u = g.document_usage("doc-1")
    assert u.cost_usd == pytest.approx(want)
    assert (u.tokens_in, u.tokens_out) == (2000, 1000)
    assert u.tier_counts == {"S": 1, "M": 1}
    assert g.document_usage("nope") is None


def test_redaction_on_every_call_including_escalation(cfg):
    p = mk(cfg, (0.1, 0.9))
    Gateway(cfg, p).complete(req())
    assert len(p.calls) == 2
    for _, prompt in p.calls:
        assert "0912 345 678" not in prompt and "Trần Thị Mai" not in prompt


def test_redaction_failure_blocks_escalation(cfg):
    n = []

    def flaky(text):
        n.append(1)
        if len(n) > 2:  # request + response of S ok; escalated request fails
            raise RuntimeError
        return text

    p = mk(cfg, (0.1, 0.9))
    with pytest.raises(GatewayError) as e:
        Gateway(cfg, p, redactor=flaky).complete(req())
    assert e.value.code == "redaction_failed" and len(p.calls) == 1


@pytest.mark.parametrize("field", ["tier_s_model", "tier_m_model"])
def test_allowlist_enforced_for_both_tiers(cfg, field):
    bad = dataclasses.replace(cfg, **{field: "evil-model"})
    p = mk(cfg, (0.9, 0.9))
    with pytest.raises(GatewayError) as e:
        Gateway(bad, p).complete(req())
    assert e.value.code == "model_not_allowed" and not p.calls


def test_env_override(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_ESCALATION_THRESHOLD", "0.5")
    monkeypatch.setenv("AI_GATEWAY_TIER_S_MODEL", "claude-sonnet-5-5")
    c = load_config()
    assert c.escalation_threshold == 0.5 and c.tier_s_model == "claude-sonnet-5-5"


def test_no_tier_is_legacy_behaviour(cfg):
    p = mk(cfg, (0.0, 0.0))
    r = Gateway(cfg, p).complete(CompletionRequest("t1", "p1", "hello"))
    assert len(p.calls) == 1 and not r.escalated
