from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


CORE_FILES = [
    "01_content_model_reference.sql",
    "02_job_zone_reference.sql",
    "03_occupation_data.sql",
    "04_scales_reference.sql",
    "14_job_zones.sql",
    "16_skills.sql",
    "28_unspsc_reference.sql",
    "29_alternate_titles.sql",
    "30_sample_of_reported_titles.sql",
    "31_technology_skills.sql",
]

IGNORE_PATTERNS = (
    r"\(\d+\)\.sql$",  # duplicated files like foo(1).sql
    r"\.part$",  # partial downloads
)


@dataclass
class SqlFile:
    path: Path
    table_name: str | None


def _extract_table_name(sql_text: str) -> str | None:
    m = re.search(r"CREATE\s+TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_text, flags=re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower()


def _is_ignored(path: Path) -> bool:
    name = path.name
    for pat in IGNORE_PATTERNS:
        if re.search(pat, name, flags=re.IGNORECASE):
            return True
    return False


def _list_sql_files(sql_dir: Path, profile: str) -> list[Path]:
    if profile == "core":
        return [sql_dir / fname for fname in CORE_FILES]
    return sorted(p for p in sql_dir.glob("*.sql") if p.is_file())


def _load_sql_file(path: Path) -> SqlFile:
    text = path.read_text(encoding="utf-8", errors="replace")
    return SqlFile(path=path, table_name=_extract_table_name(text))


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND lower(name)=lower(?) LIMIT 1",
        (table_name,),
    ).fetchone()
    return bool(row)


def _run_script(conn: sqlite3.Connection, path: Path) -> None:
    script = path.read_text(encoding="utf-8", errors="replace")
    conn.executescript(script)


def _create_helper_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_onet_occupation_code ON occupation_data(onetsoc_code);
        CREATE INDEX IF NOT EXISTS idx_onet_alt_code ON alternate_titles(onetsoc_code);
        CREATE INDEX IF NOT EXISTS idx_onet_reported_code ON sample_of_reported_titles(onetsoc_code);
        CREATE INDEX IF NOT EXISTS idx_onet_job_zone_code ON job_zones(onetsoc_code);
        CREATE INDEX IF NOT EXISTS idx_onet_tech_code ON technology_skills(onetsoc_code);

        CREATE VIEW IF NOT EXISTS onet_taxonomy_core AS
        SELECT
            o.onetsoc_code,
            o.title AS occupation_title,
            o.description AS occupation_description,
            j.job_zone,
            r.name AS job_zone_name,
            r.education AS job_zone_education,
            r.experience AS job_zone_experience
        FROM occupation_data o
        LEFT JOIN job_zones j ON j.onetsoc_code = o.onetsoc_code
        LEFT JOIN job_zone_reference r ON r.job_zone = j.job_zone;

        CREATE VIEW IF NOT EXISTS onet_title_lookup AS
        SELECT onetsoc_code, title AS candidate_title, 'occupation_title' AS source, 1 AS priority
        FROM occupation_data
        UNION ALL
        SELECT onetsoc_code, alternate_title AS candidate_title, 'alternate_title' AS source, 2 AS priority
        FROM alternate_titles
        UNION ALL
        SELECT onetsoc_code, reported_job_title AS candidate_title, 'reported_title' AS source, 3 AS priority
        FROM sample_of_reported_titles;

        CREATE VIEW IF NOT EXISTS onet_tech_skills_flat AS
        SELECT
            onetsoc_code,
            example AS technology_example,
            commodity_code,
            hot_technology,
            in_demand
        FROM technology_skills;
        """
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Import O*NET SQL dumps into SQLite.")
    ap.add_argument("--sql-dir", default="/home/afio/Scrivania/da_collab", help="Directory with O*NET .sql files")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite", help="Target SQLite DB path")
    ap.add_argument("--profile", choices=["core", "all"], default="core", help="Import subset")
    ap.add_argument("--replace", action="store_true", help="Drop and recreate existing tables for selected files")
    ap.add_argument("--dry-run", action="store_true", help="Print planned actions without writing DB")
    args = ap.parse_args()

    sql_dir = Path(args.sql_dir)
    db_path = Path(args.db)

    if not sql_dir.exists():
        raise RuntimeError(f"SQL directory not found: {sql_dir}")

    planned_paths = _list_sql_files(sql_dir, args.profile)
    if not planned_paths:
        raise RuntimeError(f"No SQL files found in {sql_dir}")

    skipped_missing = 0
    skipped_ignored = 0
    candidates: list[SqlFile] = []

    for path in planned_paths:
        if not path.exists():
            print(f"[skip-missing] {path.name}")
            skipped_missing += 1
            continue
        if _is_ignored(path):
            print(f"[skip-ignored] {path.name}")
            skipped_ignored += 1
            continue
        if path.stat().st_size == 0:
            print(f"[skip-empty] {path.name}")
            skipped_ignored += 1
            continue
        candidates.append(_load_sql_file(path))

    if not candidates:
        raise RuntimeError("No valid SQL files to import.")

    print(f"[plan] files={len(candidates)} skipped_missing={skipped_missing} skipped_ignored={skipped_ignored}")

    if args.dry_run:
        for f in candidates:
            print(f"[dry-run] {f.path.name} -> table={f.table_name or 'unknown'}")
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=OFF")

    try:
        imported = 0
        skipped_existing = 0

        for f in candidates:
            table = f.table_name
            if table and _table_exists(conn, table):
                if args.replace:
                    print(f"[replace] dropping existing table: {table}")
                    conn.execute(f"DROP TABLE IF EXISTS {table}")
                else:
                    print(f"[skip-existing] {f.path.name} (table {table} already exists)")
                    skipped_existing += 1
                    continue

            print(f"[import] {f.path.name}")
            _run_script(conn, f.path)
            imported += 1

        _create_helper_views(conn)
        conn.commit()

    finally:
        conn.close()

    print(f"Done. Imported={imported} | skipped_existing={skipped_existing}")
    print(f"DB: {db_path}")


if __name__ == "__main__":
    main()
