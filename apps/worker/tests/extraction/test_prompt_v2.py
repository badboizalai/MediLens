"""extract-v2 (S7-T61): per-Unit few-shots, line ids in the prompt, line id -> bbox in code."""

from medilens_worker.extraction.prompts import PROMPT_VERSION, extract_prompt, load_schemas
from medilens_worker.extraction.service import run_extraction

PAGES = ["Benh nhan kham rang.\nRang 36 sau o mat nhai.", "Ghi chu: hen tai kham sau 6 thang."]
BOXES = [[(0.1, 0.1, 0.9, 0.2), (0.1, 0.3, 0.8, 0.4)], [(0, 0, 1, 1)]]


class Stub:
    def __init__(self, reply):
        self.reply = reply

    def complete(self, prompt, *, max_output_tokens=4096):
        import json

        from medilens_worker.extraction.service import Completion

        return Completion(json.dumps(self.reply), "stub-model", 0.01)


def lined(lines):
    f = {
        "value": "36",
        "confidence": 0.95,
        "source": {"page": 1, "quote": "Rang 36 sau o mat nhai.", "lines": lines},
    }
    return {"encounter": {}, "teeth": [{"fdi": f, "condition": "caries"}]}


def test_version_is_v2():
    assert PROMPT_VERSION == "extract-v2"


def test_prompt_has_own_unit_fewshot_and_line_ids():
    marks = {"dental": "Nha khoa Demo", "cardiology": "Khoa Tim mach", "oncology": "mau mo Demo"}
    for unit, mark in marks.items():
        p = extract_prompt(unit, load_schemas()[unit], PAGES)
        assert mark in p and "Nguyen Van Test" in p and "[L2] Rang 36 sau" in p
        assert all(m not in p for u, m in marks.items() if u != unit)


def test_v1_prompt_still_renderable_without_fewshot():
    p = extract_prompt("dental", load_schemas()["dental"], PAGES, version="extract-v1")
    assert "Nguyen Van Test" not in p and "[L1]" not in p and "[[page 2]]" in p


def test_line_ids_become_bbox_and_lines_key_removed():
    run = run_extraction("d1", PAGES, Stub(lined([1, 2])), unit="dental", boxes=BOXES)
    src = run.result["teeth"][0]["fdi"]["source"]
    assert src["bbox"] == [0.1, 0.1, 0.9, 0.4] and "lines" not in src
    assert all(f["reason"] != "line_id_unknown" for f in run.flags)


def test_unknown_line_id_flagged_not_crashing():
    for bad in ([9], [0], ["1"], [], [True]):
        run = run_extraction("d1", PAGES, Stub(lined(bad)), unit="dental", boxes=BOXES)
        assert "bbox" not in run.result["teeth"][0]["fdi"]["source"]
        assert {"path": "$.teeth[0].fdi", "reason": "line_id_unknown"} in run.flags


def test_no_boxes_still_strips_lines():
    run = run_extraction("d1", PAGES, Stub(lined([2])), unit="dental")
    assert "lines" not in run.result["teeth"][0]["fdi"]["source"]


def test_model_supplied_bbox_is_dropped():
    from medilens_worker.extraction.service import anchor_lines

    r = {"x": {"value": "a", "confidence": 0.9, "source": {"page": 1, "bbox": [0, 0, 1, 1]}}}
    anchor_lines(r, ["a"], None)
    assert "bbox" not in r["x"]["source"]
