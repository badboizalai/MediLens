"""Front-matter + claims checks for draft KnowledgeArticles (S10-T94, BR-024).

Drafts only: status must stay draft-pending-CSO until the human CSO review (D99).
"""

import datetime
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTICLES = sorted((ROOT / "content" / "articles").glob("KA-*.md"))
REGIONS = {
    r["region_code"]
    for r in yaml.safe_load((ROOT / "data/terminology/region-tree.v1.yaml").read_text("utf-8"))
}
LINT = ROOT / ".claude/skills/medilens-regulatory-privacy-officer/scripts/claims_lint.py"
UNITS = {"dental", "cardiology", "oncology", "general"}


def load(path):
    _, fm, body = path.read_text("utf-8").split("---\n", 2)
    return yaml.safe_load(fm), body


def test_twenty_articles_with_unit_minimums():
    assert [p.stem for p in ARTICLES] == [f"KA-{i:03d}" for i in range(1, 21)]
    units = [load(p)[0]["unit"] for p in ARTICLES]
    for u in ("dental", "cardiology", "oncology"):
        assert units.count(u) >= 5, u


def test_front_matter_and_body():
    for p in ARTICLES:
        fm, body = load(p)
        assert fm["id"] == p.stem
        assert fm["unit"] in UNITS
        assert fm["title_vi"] and fm["title_en"]
        assert fm["region_codes"] and set(fm["region_codes"]) <= REGIONS, p.name
        assert fm["status"] == "draft-pending-CSO"
        assert fm["last_reviewed"] is None and fm["cso_review_date"] is None
        assert fm["reviewer"] is None
        assert isinstance(fm["review_due"], datetime.date)
        assert fm["source_verification"] == "pending"
        assert fm["sources"], "BR-024: no sources, cannot publish"
        for s in fm["sources"]:
            assert s["title"] and re.match(r"https://", s["url"]) and s["accessed"]
        assert "## Tiếng Việt" in body and "## English" in body
        assert "Hãy hỏi đội ngũ chăm sóc" in body and "**Ask your care team:**" in body
        assert "claims-ok" not in body


def test_oncology_explains_tnm_letters():
    text = " ".join(load(p)[1] for p in ARTICLES if load(p)[0]["unit"] == "oncology")
    for needle in ("T (tumour)", "N (nodes)", "M (metastasis)"):
        assert needle in text


def test_claims_lint_clean():
    r = subprocess.run(
        [sys.executable, str(LINT), str(ROOT / "content/articles")], capture_output=True, text=True
    )
    assert r.returncode == 0 and "BLOCK=0 REVIEW=0" in r.stdout, r.stdout
