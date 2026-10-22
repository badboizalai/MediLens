"""Licence gate: terminology loaders refuse to run unless the register row is approved."""

from __future__ import annotations

import csv
from pathlib import Path

REGISTER = Path(__file__).resolve().parents[2] / "license-register.csv"


class LicenceNotApproved(RuntimeError):
    """Raised when the License Register row is missing or not `approved`."""


def require_approved(lic_id: str, register: Path = REGISTER) -> None:
    with Path(register).open(newline="", encoding="utf-8") as fh:
        row = next((r for r in csv.DictReader(fh) if r["lic_id"] == lic_id), None)
    if row is None:
        raise LicenceNotApproved(f"{lic_id} not found in {register}; refusing to load.")
    if row["decision"] != "approved":
        raise LicenceNotApproved(
            f"{lic_id} ({row['source_name']}) decision is '{row['decision']}', not 'approved'. "
            "Complete licence review (data-curator + regulatory co-sign, gate G1-D) "
            "and update data/license-register.csv before loading this code list."
        )
