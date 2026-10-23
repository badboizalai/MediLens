import csv
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("hazard_risk_check.py")
ROOT = Path(__file__).resolve().parents[4]

LEGACY = dict(
    hazard_id="HZ-1",
    title="t",
    harm="h",
    severity="3",
    probability="3",
    controls="CS-001 rule",
    cs_ids="CS-001",
    residual_severity="3",
    residual_probability="1",
    owner="o",
    status="open",
    notes="",
)
PROJECT = dict(
    id="HZ-1",
    hazard="t",
    cause="c",
    harm="h",
    severity="3",
    likelihood="3",
    initial_risk="9 ALARP",
    controls="CS-001 rule; CS-002 confirm",
    residual_severity="3",
    residual_likelihood="1",
    residual_risk="3 acceptable",
    owner="o",
    status="open",
    verification="TC-TBD",
)


def run(tmp_path, row):
    f = tmp_path / "log.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row))
        w.writeheader()
        w.writerow(row)
    return subprocess.run([sys.executable, str(SCRIPT), str(f)], capture_output=True, text=True)


def test_legacy_schema_passes(tmp_path):
    r = run(tmp_path, LEGACY)
    assert r.returncode == 0 and "acceptable 1" in r.stdout


def test_project_schema_passes(tmp_path):
    r = run(tmp_path, PROJECT)
    assert r.returncode == 0 and "acceptable 1" in r.stdout


def test_project_schema_unacceptable_blocks(tmp_path):
    r = run(tmp_path, {**PROJECT, "residual_severity": "4", "residual_likelihood": "3"})
    assert r.returncode == 1 and "UNACCEPTABLE" in r.stdout


def test_project_schema_without_cs_refs_blocks(tmp_path):
    r = run(tmp_path, {**PROJECT, "controls": "manual review"})
    assert r.returncode == 1 and "empty cs_ids" in r.stdout


def test_real_hazard_log():
    log = ROOT / "safety" / "hazard-log.csv"
    r = subprocess.run([sys.executable, str(SCRIPT), str(log)], capture_output=True, text=True)
    assert "Rows: 19 | acceptable 17 | ALARP 2 | UNACCEPTABLE 0" in r.stdout
