#!/usr/bin/env python3
"""
One-shot: copy data from a local SQLite DB into a running Postgres container.

Assumes Postgres schema already exists (run alembic upgrade head / init_db first).
Uses docker exec + COPY so no extra Python DB drivers are required.

Usage:
  python3 scripts/sqlite_to_postgres.py
  python3 scripts/sqlite_to_postgres.py --sqlite backend/trainingplan.db
  python3 scripts/sqlite_to_postgres.py --container trainingplan_postgres \\
      --db trainingplan --user trainingplan_user
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sqlite3
import subprocess
import sys
from pathlib import Path


PREFERRED_ORDER = [
    "users",
    "garmin_activities",
    "garmin_hrv",
    "weekly_thresholds",
    "events",
    "training_plans",
    "workouts",
    "alembic_version",
]


def run(cmd: list[str], *, input_bytes: bytes | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=input_bytes, capture_output=True, check=check)


def psql(container: str, user: str, db: str, sql: str) -> None:
    result = run(
        ["docker", "exec", "-i", container, "psql", "-U", user, "-d", db, "-v", "ON_ERROR_STOP=1"],
        input_bytes=sql.encode("utf-8"),
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(f"psql failed ({result.returncode})")


def psql_tuples(container: str, user: str, db: str, sql: str) -> list[tuple[str, ...]]:
    result = run(
        [
            "docker",
            "exec",
            "-i",
            container,
            "psql",
            "-U",
            user,
            "-d",
            db,
            "-v",
            "ON_ERROR_STOP=1",
            "-tAc",
            sql,
        ],
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(f"psql query failed ({result.returncode})")
    lines = result.stdout.decode("utf-8", errors="replace").strip().splitlines()
    out: list[tuple[str, ...]] = []
    for line in lines:
        if not line.strip():
            continue
        out.append(tuple(line.split("|")))
    return out


def list_sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    names = [r[0] for r in rows]
    ordered = [t for t in PREFERRED_ORDER if t in names]
    ordered.extend(sorted(t for t in names if t not in ordered))
    return ordered


def sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")').fetchall()]


def pg_column_types(container: str, user: str, db: str, table: str) -> dict[str, str]:
    rows = psql_tuples(
        container,
        user,
        db,
        "SELECT column_name, data_type FROM information_schema.columns "
        f"WHERE table_schema='public' AND table_name='{table}' ORDER BY ordinal_position;",
    )
    return {name: dtype for name, dtype in rows}


def coerce_value(value, pg_type: str | None):
    if value is None:
        return None

    dtype = (pg_type or "").lower()

    if dtype in {"integer", "bigint", "smallint"}:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return int(round(value))
        s = str(value).strip()
        if s == "":
            return None
        try:
            return int(round(float(s)))
        except ValueError:
            return None

    if dtype in {"double precision", "real", "numeric"}:
        if isinstance(value, (int, float)):
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return float(value)
        s = str(value).strip()
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None

    if dtype == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        s = str(value).strip().lower()
        if s in {"1", "true", "t", "yes", "y"}:
            return True
        if s in {"0", "false", "f", "no", "n"}:
            return False
        return None

    if dtype in {"json", "jsonb"}:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        if isinstance(value, (bytes, bytearray)):
            return value.decode("utf-8", errors="replace")
        s = str(value)
        # Leave as-is if already JSON-looking; Postgres JSON accepts text
        return s

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    return value


def csv_cell(value) -> str:
    if value is None:
        return r"\N"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def export_csv(
    conn: sqlite3.Connection,
    table: str,
    columns: list[str],
    pg_types: dict[str, str],
) -> tuple[str, int]:
    cols_sql = ", ".join(f'"{c}"' for c in columns)
    rows = conn.execute(f'SELECT {cols_sql} FROM "{table}"').fetchall()
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    for row in rows:
        coerced = [coerce_value(v, pg_types.get(col)) for col, v in zip(columns, row)]
        writer.writerow([csv_cell(v) for v in coerced])
    return buf.getvalue(), len(rows)


def copy_table(
    container: str,
    user: str,
    db: str,
    table: str,
    columns: list[str],
    csv_data: str,
) -> None:
    cols = ", ".join(f'"{c}"' for c in columns)
    copy_sql = f"\\copy \"{table}\" ({cols}) FROM STDIN WITH (FORMAT csv, NULL '\\N')\n"
    payload = copy_sql + csv_data
    result = run(
        ["docker", "exec", "-i", container, "psql", "-U", user, "-d", db, "-v", "ON_ERROR_STOP=1"],
        input_bytes=payload.encode("utf-8"),
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        raise SystemExit(f"COPY failed for table {table}")


def reset_sequences(container: str, user: str, db: str, tables: list[str]) -> None:
    statements = []
    for table in tables:
        if table == "alembic_version":
            continue
        statements.append(
            f"""
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = '{table}' AND column_name = 'id'
  ) AND EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind = 'S' AND c.relname = '{table}_id_seq'
  ) THEN
    PERFORM setval(
      pg_get_serial_sequence('"{table}"', 'id'),
      COALESCE((SELECT MAX(id) FROM "{table}"), 1),
      true
    );
  END IF;
END $$;
"""
        )
    if statements:
        psql(container, user, db, "\n".join(statements))


def main() -> None:
    parser = argparse.ArgumentParser(description="Import SQLite data into local Postgres container")
    parser.add_argument(
        "--sqlite",
        default=str(Path(__file__).resolve().parents[1] / "backend" / "trainingplan.db"),
        help="Path to SQLite database file",
    )
    parser.add_argument("--container", default="trainingplan_postgres")
    parser.add_argument("--db", default="trainingplan")
    parser.add_argument("--user", default="trainingplan_user")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (TRUNCATE target tables)",
    )
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite)
    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite file not found: {sqlite_path}")

    probe = run(["docker", "inspect", "-f", "{{.State.Running}}", args.container], check=False)
    if probe.returncode != 0 or probe.stdout.decode().strip() != "true":
        raise SystemExit(
            f"Postgres container '{args.container}' is not running. "
            "Start it with: docker compose up -d postgres"
        )

    conn = sqlite3.connect(str(sqlite_path))
    try:
        tables = list_sqlite_tables(conn)
        if not tables:
            raise SystemExit("No tables found in SQLite database")

        print(f"Source: {sqlite_path}")
        print(f"Target: {args.container}/{args.db}")
        print(f"Tables: {', '.join(tables)}")
        if not args.yes:
            reply = input("This TRUNCATEs matching Postgres tables. Type 'import' to continue: ")
            if reply.strip() != "import":
                raise SystemExit("Aborted.")

        # Only truncate tables that exist on both sides
        pg_tables = {
            r[0]
            for r in psql_tuples(
                args.container,
                args.user,
                args.db,
                "SELECT tablename FROM pg_tables WHERE schemaname='public';",
            )
        }
        tables = [t for t in tables if t in pg_tables]
        if not tables:
            raise SystemExit("No overlapping tables between SQLite and Postgres")

        truncate_list = ", ".join(f'"{t}"' for t in tables)
        psql(
            args.container,
            args.user,
            args.db,
            f"SET session_replication_role = replica;\nTRUNCATE {truncate_list} CASCADE;\n",
        )

        for table in tables:
            pg_types = pg_column_types(args.container, args.user, args.db, table)
            sq_cols = sqlite_columns(conn, table)
            columns = [c for c in sq_cols if c in pg_types]
            skipped = [c for c in sq_cols if c not in pg_types]
            if skipped:
                print(f"  - {table}: skipping SQLite-only columns: {', '.join(skipped)}")
            if not columns:
                print(f"  - {table}: no shared columns (skip)")
                continue

            csv_data, count = export_csv(conn, table, columns, pg_types)
            if count == 0:
                print(f"  - {table}: 0 rows (skip)")
                continue
            copy_table(args.container, args.user, args.db, table, columns, csv_data)
            print(f"  - {table}: {count} rows")

        psql(args.container, args.user, args.db, "SET session_replication_role = DEFAULT;\n")
        reset_sequences(args.container, args.user, args.db, tables)
        print("Import complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
