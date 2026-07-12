from __future__ import annotations

import argparse
import csv
import sqlite3
import zipfile
from pathlib import Path
from typing import Any, Iterable


def _s(v: Any) -> str:
    return str(v or "").strip()


def _csv_rows_from_zip(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, str]]:
    with zf.open(member, "r") as f:
        text = f.read().decode("utf-8-sig", errors="replace").splitlines()
    reader = csv.DictReader(text)
    for row in reader:
        yield {k: _s(v) for k, v in row.items()}


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS esco_occupations (
          esco_id TEXT PRIMARY KEY,
          uri TEXT,
          preferred_label TEXT,
          alt_labels TEXT,
          isco_group TEXT,
          status TEXT,
          code TEXT,
          description TEXT
        );

        CREATE TABLE IF NOT EXISTS esco_skills (
          esco_skill_id TEXT PRIMARY KEY,
          uri TEXT,
          preferred_label TEXT,
          alt_labels TEXT,
          skill_type TEXT,
          reuse_level TEXT,
          status TEXT,
          description TEXT
        );

        CREATE TABLE IF NOT EXISTS esco_occupation_skills (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          occupation_id TEXT,
          occupation_label TEXT,
          relation_type TEXT,
          skill_type TEXT,
          skill_id TEXT,
          skill_label TEXT
        );

        CREATE INDEX IF NOT EXISTS ix_esco_occ_label ON esco_occupations(preferred_label);
        CREATE INDEX IF NOT EXISTS ix_esco_occ_isco ON esco_occupations(isco_group);
        CREATE INDEX IF NOT EXISTS ix_esco_skill_label ON esco_skills(preferred_label);
        CREATE INDEX IF NOT EXISTS ix_esco_occ_skill_occ ON esco_occupation_skills(occupation_id);
        CREATE INDEX IF NOT EXISTS ix_esco_occ_skill_skill ON esco_occupation_skills(skill_id);
        """
    )


def _uri_to_id(uri: str) -> str:
    u = _s(uri)
    if not u:
        return ""
    return u.rsplit("/", 1)[-1]


def import_occupations(conn: sqlite3.Connection, zf: zipfile.ZipFile, member: str) -> int:
    n = 0
    for row in _csv_rows_from_zip(zf, member):
        esco_id = _uri_to_id(row.get("conceptUri"))
        if not esco_id:
            continue
        conn.execute(
            """
            INSERT INTO esco_occupations(
              esco_id, uri, preferred_label, alt_labels, isco_group, status, code, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(esco_id) DO UPDATE SET
              uri=excluded.uri,
              preferred_label=excluded.preferred_label,
              alt_labels=excluded.alt_labels,
              isco_group=excluded.isco_group,
              status=excluded.status,
              code=excluded.code,
              description=excluded.description
            """,
            (
                esco_id,
                _s(row.get("conceptUri")),
                _s(row.get("preferredLabel")),
                _s(row.get("altLabels")),
                _s(row.get("iscoGroup")),
                _s(row.get("status")),
                _s(row.get("code")),
                _s(row.get("description")),
            ),
        )
        n += 1
    return n


def import_skills(conn: sqlite3.Connection, zf: zipfile.ZipFile, member: str) -> int:
    n = 0
    for row in _csv_rows_from_zip(zf, member):
        skill_id = _uri_to_id(row.get("conceptUri"))
        if not skill_id:
            continue
        conn.execute(
            """
            INSERT INTO esco_skills(
              esco_skill_id, uri, preferred_label, alt_labels, skill_type, reuse_level, status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(esco_skill_id) DO UPDATE SET
              uri=excluded.uri,
              preferred_label=excluded.preferred_label,
              alt_labels=excluded.alt_labels,
              skill_type=excluded.skill_type,
              reuse_level=excluded.reuse_level,
              status=excluded.status,
              description=excluded.description
            """,
            (
                skill_id,
                _s(row.get("conceptUri")),
                _s(row.get("preferredLabel")),
                _s(row.get("altLabels")),
                _s(row.get("skillType")),
                _s(row.get("reuseLevel")),
                _s(row.get("status")),
                _s(row.get("description")),
            ),
        )
        n += 1
    return n


def import_occ_skill_rel(conn: sqlite3.Connection, zf: zipfile.ZipFile, member: str) -> int:
    conn.execute("DELETE FROM esco_occupation_skills")
    n = 0
    for row in _csv_rows_from_zip(zf, member):
        occ_id = _uri_to_id(row.get("occupationUri"))
        skill_id = _uri_to_id(row.get("skillUri"))
        if not occ_id or not skill_id:
            continue
        conn.execute(
            """
            INSERT INTO esco_occupation_skills(
              occupation_id, occupation_label, relation_type, skill_type, skill_id, skill_label
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                occ_id,
                _s(row.get("occupationLabel")),
                _s(row.get("relationType")),
                _s(row.get("skillType")),
                skill_id,
                _s(row.get("skillLabel")),
            ),
        )
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Import ESCO CSV zip (occupations/skills/relations) into SQLite")
    ap.add_argument("--db", default="data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite")
    ap.add_argument("--zip", required=True, help="Path to ESCO CSV zip")
    ap.add_argument("--occupations-file", default="occupations_en.csv")
    ap.add_argument("--skills-file", default="skills_en.csv")
    ap.add_argument("--relations-file", default="occupationSkillRelations_en.csv")
    args = ap.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.exists():
        raise RuntimeError(f"ESCO zip not found: {zip_path}")

    conn = sqlite3.connect(args.db)
    try:
        ensure_tables(conn)
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
            for n in (args.occupations_file, args.skills_file, args.relations_file):
                if n not in names:
                    raise RuntimeError(f"Missing member in zip: {n}")

            n_occ = import_occupations(conn, zf, args.occupations_file)
            n_sk = import_skills(conn, zf, args.skills_file)
            n_rel = import_occ_skill_rel(conn, zf, args.relations_file)
        conn.commit()
    finally:
        conn.close()

    print(f"DB: {args.db}")
    print(f"ZIP: {zip_path}")
    print(f"Imported occupations: {n_occ}")
    print(f"Imported skills: {n_sk}")
    print(f"Imported occupation-skill relations: {n_rel}")


if __name__ == "__main__":
    main()
