"""Reuse the format checks of the clinical-informaticist skill (single source of truth)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[3]
    / ".claude/skills/medilens-clinical-informaticist/scripts/fhir_bundle_check.py"
)
_spec = importlib.util.spec_from_file_location("_fhir_bundle_check", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

check_code = _mod.check_code
luhn_check_digit = _mod.luhn_check_digit
