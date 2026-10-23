"""Tests for tools/check_contracts.py (one valid and one invalid example)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import check_contracts as c  # noqa: E402

SCHEMA = {
    "type": "object",
    "required": ["a"],
    "additionalProperties": False,
    "properties": {"a": {"type": "integer"}},
}


def setup(tmp_path, valid, invalid):
    (tmp_path / "x.schema.json").write_text(json.dumps(SCHEMA))
    (tmp_path / "examples").mkdir()
    (tmp_path / "examples/x.valid.json").write_text(json.dumps(valid))
    (tmp_path / "examples/x.invalid.json").write_text(json.dumps(invalid))
    return tmp_path


def test_good_examples_pass(tmp_path):
    assert c.check(setup(tmp_path, {"a": 1}, {"a": "no"})) == []


def test_misclassified_examples_fail(tmp_path):
    assert len(c.check(setup(tmp_path, {"a": "no"}, {"a": 1}))) == 2


def test_repo_contracts_ok():
    assert c.check() == []
