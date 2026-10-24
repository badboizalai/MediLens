"""Daily metrics-mart job: refresh analytics.* from OLTP, load eval scores, run DQ checks.

    DATABASE_URL=... python -m marts.run [--eval-csv eval_scores.csv]   (cwd: data/)

Needs a role that can read clinical.* across profiles (RLS) and write analytics.*; the job only
ever writes aggregates. Exit code 1 when any DQ check fails.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

import psycopg

HERE = Path(__file__).parent


def load_eval(conn: psycopg.Connection, csv_path: Path) -> int:
    """Upsert offline eval reports (ml/eval): columns report_date,prompt_version,cer,field_f1."""
    with csv_path.open(newline="") as fh:
        rows = [
            (r["report_date"], r["prompt_version"], float(r["cer"]), float(r["field_f1"]))
            for r in csv.DictReader(fh)
        ]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO analytics.eval_scores VALUES (%s, %s, %s, %s) ON CONFLICT "
            "(report_date, prompt_version) DO UPDATE SET cer = excluded.cer, "
            "field_f1 = excluded.field_f1",
            rows,
        )
    return len(rows)


def refresh(conn: psycopg.Connection) -> None:
    for name in ("01_schema.sql", "02_refresh.sql"):
        conn.execute((HERE / "sql" / name).read_text())


def failed_checks(conn: psycopg.Connection) -> dict[str, int]:
    rows = conn.execute((HERE / "dq" / "checks.sql").read_text()).fetchall()
    return {name: n for name, n in rows if n}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval-csv", type=Path)
    ap.add_argument("--check-only", action="store_true", help="DQ + freshness, no refresh")
    ap.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args(argv)
    if not args.dsn:
        ap.error("set DATABASE_URL or --dsn")
    with psycopg.connect(args.dsn, autocommit=False) as conn:
        if not args.check_only:
            refresh(conn)
        if args.eval_csv and not args.check_only:
            load_eval(conn, args.eval_csv)
        bad = failed_checks(conn)
        if bad:
            conn.rollback()  # never publish a mart that failed DQ
            print(f"DQ FAILED: {bad}", file=sys.stderr)
            return 1
        conn.commit()
    print("metrics mart refreshed, DQ ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
