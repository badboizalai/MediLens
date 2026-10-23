"""ICD-10 path: interface only. Refuses while the licence gate (LIC-002) is not approved."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from ..anatomy.fdi import TERMINOLOGY_DIR

# Reuse the loaders' gate (data/terminology/loaders/licence.py) by file path: `loaders` is not a package of the worker.
_spec = importlib.util.spec_from_file_location(
    "_medilens_licence_gate", TERMINOLOGY_DIR / "loaders" / "licence.py"
)
assert _spec and _spec.loader
_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gate)

LicenceNotApproved = _gate.LicenceNotApproved


def to_icd10(text: str, register: Path | None = None):
    """Free text -> ICD-10 code. Raises LicenceNotApproved until LIC-002 is approved (gate G1-D)."""
    _gate.require_approved("LIC-002", *([register] if register else []))
    # No ICD-10 list is bundled; the owner-provided file loads through loaders.icd10 in a later task.
    raise NotImplementedError("ICD-10 mapping is not implemented yet")
