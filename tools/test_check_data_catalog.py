"""Tests for tools/check_data_catalog.py (synthetic migrations only)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import check_data_catalog as c  # noqa: E402

MIG = '''
_STD = """created_at timestamptz, deleted_at timestamptz"""
_PK = "id uuid PRIMARY KEY"
_TABLES = [
    ("identity.users", "external_sub text NOT NULL UNIQUE, ref numeric(10,6), UNIQUE (a, b)"),
]
def upgrade():
    op.execute("""
CREATE TABLE audit.ev (
  id uuid NOT NULL, ip inet,
  PRIMARY KEY (id, at)
) PARTITION BY RANGE (at)""")
    op.execute("ALTER TABLE identity.users ADD COLUMN IF NOT EXISTS nick text")
'''


def write(tmp_path, text=MIG):
    (tmp_path / "0001_x.py").write_text(text)
    return tmp_path


def test_extracts_columns_from_all_patterns(tmp_path):
    cols = c.migration_columns(write(tmp_path))
    assert ("identity.users", "external_sub") in cols
    assert ("identity.users", "ref") in cols
    assert ("identity.users", "id") in cols
    assert ("identity.users", "created_at") in cols
    assert ("audit.ev", "ip") in cols
    assert ("identity.users", "nick") in cols
    assert ("identity.users", "UNIQUE") not in cols
    assert ("audit.ev", "PRIMARY") not in cols


def catalog(tmp_path, rows):
    p = tmp_path / "columns.csv"
    p.write_text("table,column,class,category,retention,owner,source,export\n" + rows)
    return p


ROW = "{t},{c},C2,internal,r,o,s,keep\n"


def test_missing_column_is_reported(tmp_path):
    cat = catalog(tmp_path, ROW.format(t="identity.users", c="status"))
    errs = c.check({("identity.users", "nick")}, cat)
    assert any("identity.users.nick" in e for e in errs)


def test_complete_catalog_passes(tmp_path):
    cat = catalog(tmp_path, ROW.format(t="identity.users", c="nick"))
    assert c.check({("identity.users", "nick")}, cat) == []


def test_invalid_class_is_reported(tmp_path):
    cat = catalog(tmp_path, "t.a,b,C9,phi,r,o,s,keep\n")
    assert any("class" in e for e in c.check(set(), cat))


def test_invalid_export_is_reported(tmp_path):
    cat = catalog(tmp_path, "t.a,b,C4,phi,r,o,s,leak\n")
    assert any("export" in e for e in c.check(set(), cat))


def test_main_exit_codes(tmp_path):
    cat = catalog(tmp_path, ROW.format(t="identity.users", c="status"))
    (tmp_path / "m").mkdir()
    mig = write(tmp_path / "m")
    assert c.main([str(mig), str(cat)]) == 1
    empty = tmp_path / "none"
    empty.mkdir()
    assert c.main([str(empty), str(cat)]) == 0
