#!/usr/bin/env python3
"""Fail if an Alembic migration adds a column that is absent from data/catalog/columns.csv.

Usage: check_data_catalog.py [MIGRATIONS_DIR] [CATALOG_CSV]

Understands three patterns in migration files: a module-level `_TABLES` list of
(name, column-definitions) with shared `_STD`/`_PK` strings, literal `CREATE TABLE x (...)`
statements, and `ALTER TABLE x ADD COLUMN y`. Stdlib only.
"""

import ast
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MIGRATIONS = ROOT / "apps/api/migrations/versions"
DEFAULT_CATALOG = ROOT / "data/catalog/columns.csv"
CLASSES = {"C0", "C1", "C2", "C3", "C4"}
CATEGORIES = {"phi", "pii", "pseudonymised", "public", "internal"}
EXPORTS = {"hash", "drop", "band", "keep"}
REQUIRED = ["table", "column", "class", "category", "retention", "owner", "source", "export"]
_CONSTRAINT = {"UNIQUE", "PRIMARY", "CONSTRAINT", "FOREIGN", "CHECK", "EXCLUDE", "LIKE"}
_CREATE = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?([\w.]+)\s*\(", re.I)
_ADD = re.compile(r"ALTER TABLE (?:ONLY )?([\w.]+)\s+ADD COLUMN (?:IF NOT EXISTS )?(\w+)", re.I)


def _split_top(body: str) -> list[str]:
    parts, depth, cur = [], 0, []
    for ch in body:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def _names(table: str, defs: str) -> set[tuple[str, str]]:
    out = set()
    for part in _split_top(defs):
        words = part.split()
        if words and words[0].upper() not in _CONSTRAINT:
            out.add((table, words[0].strip('"')))
    return out


def _balanced(text: str, start: int) -> str:
    depth = 1
    for i in range(start, len(text)):
        depth += text[i] == "("
        depth -= text[i] == ")"
        if depth == 0:
            return text[start:i]
    return text[start:]


def _file_columns(path: Path) -> set[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    consts: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign | ast.AnnAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for t in targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = value
    cols: set[tuple[str, str]] = set()
    shared = f"{consts.get('_PK', '')}, {consts.get('_STD', '')}".strip(", ")
    for name, defs in consts.get("_TABLES", []):
        cols |= _names(name, f"{shared}, {defs}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
            for m in _CREATE.finditer(text):
                cols |= _names(m.group(1), _balanced(text, m.end()))
            for m in _ADD.finditer(text):
                cols.add((m.group(1), m.group(2)))
    return cols


def migration_columns(directory: Path) -> set[tuple[str, str]]:
    cols: set[tuple[str, str]] = set()
    for path in sorted(Path(directory).glob("*.py")):
        cols |= _file_columns(path)
    return cols


def check(cols: set[tuple[str, str]], catalog: Path) -> list[str]:
    errors, seen = [], set()
    with open(catalog, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [h for h in REQUIRED if h not in (reader.fieldnames or [])]
        if missing:
            return [f"catalog missing header(s): {', '.join(missing)}"]
        for n, row in enumerate(reader, start=2):
            key = (row["table"], row["column"])
            where = f"columns.csv:{n} {key[0]}.{key[1]}"
            if key in seen:
                errors.append(f"{where}: duplicate entry")
            seen.add(key)
            for field, allowed in (
                ("class", CLASSES),
                ("category", CATEGORIES),
                ("export", EXPORTS),
            ):
                if row[field] not in allowed:
                    errors.append(f"{where}: invalid {field} '{row[field]}'")
            for field in ("retention", "owner", "source"):
                if not row[field].strip():
                    errors.append(f"{where}: empty {field}")
    errors += [f"not in catalog: {t}.{c}" for t, c in sorted(cols - seen)]
    return errors


def main(argv: list[str]) -> int:
    mig = Path(argv[0]) if argv else DEFAULT_MIGRATIONS
    cat = Path(argv[1]) if len(argv) > 1 else DEFAULT_CATALOG
    if not mig.is_dir():
        print(f"no migrations at {mig}; nothing to check")
        return 0
    cols = migration_columns(mig)
    errors = check(cols, cat)
    for e in errors:
        print(e)
    print(f"{len(cols)} migration columns checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
