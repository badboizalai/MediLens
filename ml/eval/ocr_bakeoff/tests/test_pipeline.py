import json
from pathlib import Path

from bakeoff import report
from bakeoff.engines import EngineUnavailable, LlmVisionEngine, OcrResult
from bakeoff.golden import load_pages
from bakeoff.runner import compute_usd, run_engine


def make_golden(tmp: Path) -> tuple[Path, Path]:
    (tmp / "records").mkdir()
    (tmp / "images").mkdir()
    rows = [("d1", "vi", "good", False), ("d2", "en", "poor", True)]
    gold, refs = [], []
    for doc, lang, q, deg in rows:
        images = [{"variant": "clean", "file": f"images/{doc}_clean.jpg"}]
        (tmp / images[0]["file"]).write_bytes(b"x")
        if deg:
            images.append({"variant": "degraded", "file": f"images/{doc}_degraded.jpg"})
        rec = {"doc_id": doc, "metadata": {"lang": lang, "images": images}}
        (tmp / "records" / f"{doc}.json").write_text(json.dumps(rec))
        gold.append(json.dumps({"doc_id": doc, "quality": q, "unit": "dental", "fields": {}}))
        refs.append(json.dumps({"doc_id": doc, "text": "Răng 24"}, ensure_ascii=False))
    (tmp / "gold.jsonl").write_text("\n".join(gold))
    ref = tmp / "ref.jsonl"
    ref.write_text("\n".join(refs), encoding="utf-8")
    return tmp, ref


class Fake:
    name = "fake"

    def __init__(self, text="Răng 24"):
        self.text = text

    def load(self):
        pass

    def recognize(self, image):
        return OcrResult(self.text)


class Missing(Fake):
    name = "missing"

    def load(self):
        raise EngineUnavailable("no weights")


def test_load_pages_prefers_degraded(tmp_path):
    golden, ref = make_golden(tmp_path)
    pages = load_pages(golden, ref)
    assert [p.image.name for p in pages] == ["d1_clean.jpg", "d2_degraded.jpg"]
    assert pages[1].quality == "poor" and pages[1].lang == "en"


def test_run_engine_perfect_and_imperfect(tmp_path):
    pages = load_pages(*make_golden(tmp_path))
    assert run_engine(Fake(), pages)["cer"]["overall"] == 0.0
    res = run_engine(Fake("Rang 24"), pages)
    assert res["cer"]["overall"] > 0 and res["usd_per_doc"] > 0
    assert res["cer"]["by_quality"].keys() == {"good", "poor"}


def test_unavailable_engine_is_not_run_with_error(tmp_path):
    res = run_engine(Missing(), load_pages(*make_golden(tmp_path)))
    assert res == {"engine": "missing", "status": "not run", "error": "no weights"}


def test_llm_engine_without_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        LlmVisionEngine().load()
    except EngineUnavailable as e:
        assert "ANTHROPIC_API_KEY" in str(e)
    else:
        raise AssertionError("expected EngineUnavailable")


def test_compute_usd():
    assert compute_usd(3600, 0.10) == 0.10


def test_report_marks_not_run_and_never_invents(tmp_path):
    pages = load_pages(*make_golden(tmp_path))
    results = [run_engine(Fake(), pages), run_engine(Missing(), pages)]
    md = report.render(results, {"golden": "g", "pages": 2, "hardware": "h", "python": "3"})
    assert "not run" in md and "no weights" in md
    assert "**fake** has the lowest overall CER" in md
    assert "optimistic" in md
