import json
from pathlib import Path

from bakeoff import engines, report
from bakeoff.engines import EngineUnavailable, LlmVisionEngine, OcrResult, load_config
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
            for v in ("degraded", "handwriting"):
                (tmp / f"images/{doc}_{v}.jpg").write_bytes(b"x")
                images.append({"variant": v, "file": f"images/{doc}_{v}.jpg"})
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


def test_load_pages_returns_every_variant(tmp_path):
    golden, ref = make_golden(tmp_path)
    pages = load_pages(golden, ref)
    assert [(p.doc_id, p.variant) for p in pages] == [
        ("d1", "clean"),
        ("d2", "clean"),
        ("d2", "degraded"),
        ("d2", "handwriting"),
    ]
    assert pages[2].image.name == "d2_degraded.jpg"
    assert pages[2].quality == "poor" and pages[2].lang == "en"


def test_run_engine_perfect_and_imperfect(tmp_path):
    pages = load_pages(*make_golden(tmp_path))
    assert run_engine(Fake(), pages)["cer"]["overall"] == 0.0
    res = run_engine(Fake("Rang 24"), pages)
    assert res["cer"]["overall"] > 0 and res["usd_per_doc"] > 0
    assert res["cer"]["by_quality"].keys() == {"good", "poor"}
    assert res["cer"]["by_variant"].keys() == {"clean", "degraded", "handwriting"}


def test_per_page_rows_have_required_fields(tmp_path):
    res = run_engine(Fake("Rang 24"), load_pages(*make_golden(tmp_path)))
    assert len(res["rows"]) == 4
    row = res["rows"][0]
    for key in ("doc_id", "unit", "lang", "quality", "variant", "engine", "cer", "latency_s"):
        assert key in row
    assert row["engine"] == "fake" and row["cer"] == row["edits"] / row["chars"] > 0


def test_llm_config_comes_from_toml(tmp_path):
    cfg = tmp_path / "c.toml"
    cfg.write_text('[llm_vision]\nmodel = "m-x"\nusd_in_per_mtok = 2\nusd_out_per_mtok = 10\n')
    e = LlmVisionEngine(load_config(cfg)["llm_vision"])
    assert e.model == "m-x" and e.usd_in == 2e-6 and e.usd_out == 1e-5


def test_default_llm_model_is_haiku_5_5_not_in_code():
    assert LlmVisionEngine().model == "claude-haiku-5-5"
    assert "claude-haiku" not in Path(engines.__file__).read_text()


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
    assert "CER by image variant" in md and "handwriting (n=1)" in md
