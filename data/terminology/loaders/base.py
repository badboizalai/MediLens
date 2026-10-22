"""Shared loader: licence gate, then read a local owner-provided CSV, validate every code."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from ._codecheck import check_code
from .licence import REGISTER, require_approved


class InvalidCodeFile(ValueError):
    """Raised when the provided file has bad headers, bad codes or duplicates."""


@dataclass(frozen=True)
class Loader:
    lic_id: str
    system: str  # "ICD-10" | "LOINC"
    code_column: str
    columns: tuple[str, ...]

    def load(self, path: Path, register: Path = REGISTER) -> list[dict[str, str]]:
        require_approved(self.lic_id, register)
        with Path(path).open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            missing = set(self.columns) - set(reader.fieldnames or [])
            if missing:
                raise InvalidCodeFile(f"missing columns: {sorted(missing)}")
            rows, seen, errors = [], set(), []
            for n, row in enumerate(reader, start=2):
                code = (row[self.code_column] or "").strip()
                err = check_code(self.system, code)
                if err is None and code in seen:
                    err = f"duplicate code '{code}'"
                if err:
                    errors.append(f"line {n}: {err}")
                seen.add(code)
                rows.append({**row, self.code_column: code})
        if errors:
            raise InvalidCodeFile("; ".join(errors))
        return rows
