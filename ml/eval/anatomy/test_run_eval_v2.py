"""Sanity checks for the golden-v2 region runner (run with apps/worker deps)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from run_eval_v2 import evaluate  # noqa: E402


def test_v2_runner_counts_and_dental_is_exact():
    g = evaluate()["groups"]
    assert g["ALL"]["total"] == 1705  # 785 teeth + 380 cardiology + 540 oncology gold regions
    assert g["unit=dental"]["accuracy"] == 1.0
    assert g["ALL"]["correct"] <= g["ALL"]["total"]
