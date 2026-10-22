import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_manifests as mk  # noqa: E402
import verify_manifests as vf  # noqa: E402


def test_committed_manifests_match_datasets():
    for name in mk.DEFAULT:
        assert vf.verify(name) == []


def test_manifest_line_format():
    line = (mk.HERE / "SHA256SUMS.golden-v0").read_text(encoding="utf-8").splitlines()[0]
    digest, rel = line.split("  ", 1)
    assert digest == hashlib.sha256((mk.EVAL / "golden-v0" / rel).read_bytes()).hexdigest()


def test_verify_detects_tamper_missing_extra(tmp_path, monkeypatch):
    ds = tmp_path / "ds"
    ds.mkdir()
    (ds / "a.txt").write_text("a")
    (ds / "b.txt").write_text("b")
    monkeypatch.setattr(mk, "EVAL", tmp_path)
    monkeypatch.setattr(mk, "HERE", tmp_path)
    (tmp_path / "SHA256SUMS.ds").write_text(
        "".join(f"{h}  {r}\n" for r, h in mk.entries(ds).items())
    )
    assert vf.verify("ds") == []
    (ds / "a.txt").write_text("changed")
    (ds / "c.txt").write_text("new")
    (ds / "b.txt").unlink()
    errs = vf.verify("ds")
    assert any("MISMATCH a.txt" in e for e in errs)
    assert any("EXTRA c.txt" in e for e in errs)
    assert any("MISSING b.txt" in e for e in errs)
