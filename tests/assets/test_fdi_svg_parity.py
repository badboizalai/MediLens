"""The 32 permanent teeth must agree across fdi.csv, the worker FDI parser and odontogram.svg ids (S8-T78)."""

import csv
import re
import sys
import xml.etree.ElementTree as ET  # trusted, repo-owned file
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps/worker/src"))
from medilens_worker.anatomy.fdi import parse_fdi  # noqa: E402

CSV = ROOT / "data/terminology/fdi.csv"
SVG = ROOT / "packages/anatomy-assets/svg/odontogram.svg"


def test_csv_worker_parser_and_svg_agree_on_32_permanent_teeth():
    with CSV.open(encoding="utf-8", newline="") as f:
        csv_codes = {r["fdi"] for r in csv.DictReader(f) if r["dentition"] == "permanent"}
    assert len(csv_codes) == 32
    svg_codes = {
        m.group(1)
        for e in ET.parse(SVG).getroot().iter()
        if (m := re.fullmatch(r"tooth_(\d\d)", e.get("id") or ""))
    }
    assert svg_codes == csv_codes
    for code in sorted(csv_codes):
        assert parse_fdi(f"tooth {code}") == [code]
