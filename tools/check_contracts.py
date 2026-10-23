"""Validate docs/architecture/contracts: each schema is valid and examples/<schema>.*.json validate
(files named *.invalid.json must be rejected).
Run: uv run --with jsonschema python tools/check_contracts.py"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

DIR = Path(__file__).resolve().parent.parent / "docs/architecture/contracts"


def check(directory: Path = DIR) -> list[str]:
    errors: list[str] = []
    validators = {}
    for p in sorted(directory.glob("*.schema.json")):
        try:
            s = json.loads(p.read_text())
            Draft202012Validator.check_schema(s)
            validators[p.name.removesuffix(".schema.json")] = Draft202012Validator(
                s, format_checker=FormatChecker()
            )
        except Exception as e:  # noqa: BLE001 - report any bad schema file
            errors.append(f"{p.name}: invalid schema: {e}")
    for ex in sorted((directory / "examples").glob("*.json")):
        stem, _, kind = ex.name.removesuffix(".json").rpartition(".")
        v = validators.get(stem)
        if v is None:
            errors.append(f"{ex.name}: no schema '{stem}'")
        elif v.is_valid(json.loads(ex.read_text())) == (kind == "invalid"):
            errors.append(f"{ex.name}: expected {'invalid' if kind == 'invalid' else 'valid'}")
    return errors


if __name__ == "__main__":
    errs = check()
    print("\n".join(errs) or "contracts ok")
    sys.exit(1 if errs else 0)
