import csv
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("defusedxml")
SCRIPT = Path(__file__).with_name("svg_region_check.py")


def run(tmp_path, svg):
    f = tmp_path / "b.svg"
    f.write_text(svg, encoding="utf-8")
    r = tmp_path / "r.csv"
    with r.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["region_code", "svg_required"])
        w.writerow(["head", "yes"])
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(f), "--regions", str(r)],
        capture_output=True,
        text=True,
    )


def test_valid_svg_passes(tmp_path):
    p = run(tmp_path, '<svg xmlns="http://www.w3.org/2000/svg"><g id="head"/></svg>')
    assert p.returncode == 0, p.stdout


def test_xxe_payload_rejected(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET")
    svg = (
        f'<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY x SYSTEM "file://{secret}">]>'
        '<svg xmlns="http://www.w3.org/2000/svg"><g id="head"><text>&x;</text></g></svg>'
    )
    p = run(tmp_path, svg)
    assert p.returncode != 0
    assert "TOP-SECRET" not in p.stdout + p.stderr
