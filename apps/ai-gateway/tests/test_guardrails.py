import json
import logging
from pathlib import Path

import pytest
from medilens_ai_gateway.config import load_config
from medilens_ai_gateway.gateway import CompletionRequest, Gateway
from medilens_ai_gateway.guardrails import check_input, check_output, classify_input
from medilens_ai_gateway.providers import StubProvider

# Synthetic questions only.
_FILE = Path(__file__).parent / "data" / "guardrail-cases.v1.jsonl"
CASES = [json.loads(line) for line in _FILE.read_text("utf-8").splitlines()]


def _got(c):
    return classify_input(c["text"]) or "none"


def test_starter_set_size_and_accuracy():
    assert len(CASES) >= 60
    bad = [(c["text"], _got(c)) for c in CASES if _got(c) != c["expected"]]
    assert 1 - len(bad) / len(CASES) >= 0.95, bad


def test_emergency_recall_is_100_percent():
    em = [c for c in CASES if c["expected"] == "emergency"]
    assert len(em) >= 10
    assert [c["text"] for c in em if _got(c) != "emergency"] == []


def test_no_benign_false_blocks():
    benign = [c for c in CASES if c["expected"] == "none"]
    assert len(benign) >= 15
    assert [c["text"] for c in benign if _got(c) != "none"] == []


class Boom:
    def complete(self, **kw):
        raise AssertionError("provider must not be called")


class Say:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def complete(self, **kw):
        self.calls += 1
        r = StubProvider().complete(**kw)
        return type(r)(**{**r.__dict__, "text": self.text})


def qa(prompt, **kw):
    return CompletionRequest("t1", "p1", prompt, traffic="qa", **kw)


def test_emergency_short_circuits_with_115_first_vi_and_en():
    gw = Gateway(load_config(), Boom())
    r = gw.complete(qa("đau ngực dữ dội"))
    assert r.guardrail == {"category": "emergency", "action": "emergency"}
    assert r.text.startswith("Hãy gọi 115") and r.cost_usd == 0
    r = gw.complete(qa("chest pain", locale="en"))
    assert r.text.startswith("Call 115")


@pytest.mark.parametrize("p,cat", [("bao nhiêu mg", "dosing"), ("sống được bao lâu", "prognosis")])
def test_blocked_input_never_reaches_provider(p, cat):
    r = Gateway(load_config(), Boom()).complete(qa(p))
    assert r.guardrail == {"category": cat, "action": "blocked_input"}
    assert "bác sĩ" in r.text


@pytest.mark.parametrize(
    "ans,cat",
    [
        ("Bạn nên uống 500 mg mỗi ngày.", "dosing"),
        ("Take 2 tablets, 3 times a day.", "dosing"),
        ("You have only 6 months to live.", "prognosis"),
        ("Bạn bị ung thư phổi.", "diagnosis"),
    ],
)
def test_unsafe_output_replaced(ans, cat):
    r = Gateway(load_config(), Say(ans)).complete(qa("giải thích kết quả"))
    assert r.guardrail == {"category": cat, "action": "blocked_output"}
    assert ans not in r.text


def test_safe_explanation_and_lab_units_pass():
    gw = Gateway(load_config(), Say("Glucose 126 mg/dL là chỉ số đường huyết trong báo cáo."))
    r = gw.complete(qa("LVEF là gì?"))
    assert r.guardrail is None and "mg/dL" in r.text


def test_non_qa_traffic_untouched():
    p = Say("500 mg")
    r = Gateway(load_config(), p).complete(CompletionRequest("t1", "p1", "đau ngực"))
    assert p.calls == 1 and r.guardrail is None


def test_guardrail_log_has_no_prompt(caplog):
    caplog.set_level(logging.INFO, logger="medilens.ai_gateway")
    Gateway(load_config(), Boom()).complete(qa("đau ngực dữ dội"))
    assert "guardrail category=emergency" in caplog.text and "ngực" not in caplog.text


def test_check_helpers_pass_clean_text():
    assert check_input("LVEF là gì?") is None
    assert check_output("EF là phân suất tống máu.") is None
