import sys
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "data"))
from marts import run  # noqa: E402


def _dsn(url: str) -> str:
    return url.replace("postgresql+psycopg://", "postgresql://")


@pytest.fixture
def seeded(migrated_url: str) -> Iterator[str]:
    """Superuser connection bypasses RLS, as the real job role must. Synthetic ids only."""
    dsn = _dsn(migrated_url)
    with psycopg.connect(dsn, autocommit=True) as c:
        uid = c.execute(
            "INSERT INTO identity.users (external_sub) VALUES ('t') RETURNING id"
        ).fetchone()[0]
        pid = c.execute(
            "INSERT INTO identity.patient_profiles (owner_user_id) VALUES (%s) RETURNING id", (uid,)
        ).fetchone()[0]
        docs = {}
        for st in ("needs_review", "needs_retake", "failed", "confirmed"):
            docs[st] = c.execute(
                "INSERT INTO clinical.documents (profile_id, storage_key, sha256, mime, status) "
                "VALUES (%s, %s, %s, 'image/png', %s) RETURNING id",
                (pid, f"k-{st}", f"h-{st}", st),
            ).fetchone()[0]
        run_id = c.execute(
            "INSERT INTO clinical.extraction_runs (profile_id, document_id, model, prompt_version, "
            "cost_usd, status) VALUES (%s, %s, 'm1', 'p1', 0.5, 'completed') RETURNING id",
            (pid, docs["needs_review"]),
        ).fetchone()[0]
        for path, val, uval, conf in (
            ("a", "x", "x", True),  # confirmed unchanged
            ("b", "x", "y", True),  # corrected
            ("c", "x", None, False),  # not reviewed
        ):
            c.execute(
                "INSERT INTO clinical.extraction_fields (profile_id, run_id, field_path, value, "
                "user_value, confirmed_at) VALUES (%s, %s, %s, %s, %s, "
                + ("now()" if conf else "NULL")
                + ")",
                (pid, run_id, path, val, uval),
            )
    yield dsn
    with psycopg.connect(dsn, autocommit=True) as c:
        c.execute("DROP SCHEMA IF EXISTS analytics CASCADE")  # not owned by migrations


def test_metrics_and_dq_pass(seeded: str, tmp_path: Path) -> None:
    ev = tmp_path / "eval.csv"
    ev.write_text("report_date,prompt_version,cer,field_f1\n2026-10-01,p1,0.05,0.9\n")
    assert run.main(["--dsn", seeded, "--eval-csv", str(ev)]) == 0
    with psycopg.connect(seeded) as c:
        row = c.execute(
            "SELECT runs, docs, cost_usd, usd_per_doc, fields_total, fields_reviewed, "
            "fields_corrected, correction_rate, confirm_rate FROM analytics.mart_run_metrics"
        ).fetchone()
        st = c.execute(
            "SELECT docs, needs_retake_rate, failed_rate FROM analytics.mart_doc_status"
        ).fetchone()
        assert c.execute("SELECT count(*) FROM analytics.eval_scores").fetchone()[0] == 1
    assert row[:2] == (1, 1) and float(row[2]) == 0.5 and float(row[3]) == 0.5
    assert row[4:7] == (3, 2, 1) and row[7] == 0.5 and row[8] == pytest.approx(2 / 3)
    assert st == (4, 0.25, 0.25)


def test_dq_fails_on_bad_eval_and_negative_cost(seeded: str, tmp_path: Path) -> None:
    ev = tmp_path / "eval.csv"
    ev.write_text("report_date,prompt_version,cer,field_f1\n2026-10-01,p1,0.05,1.7\n")
    assert run.main(["--dsn", seeded, "--eval-csv", str(ev)]) == 1
    with psycopg.connect(seeded, autocommit=True) as c:
        c.execute("UPDATE clinical.extraction_runs SET cost_usd = -1")
    assert run.main(["--dsn", seeded]) == 1


def test_check_only_flags_never_refreshed(seeded: str) -> None:
    with psycopg.connect(seeded, autocommit=True) as c:
        for name in ("01_schema.sql",):
            c.execute((run.HERE / "sql" / name).read_text())
    assert run.main(["--dsn", seeded, "--check-only"]) == 1
