from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from jobintel_next.product.alerts import per_user_runs_dir

from .service import check_new_matches, is_saved_search_due, list_saved_searches


def _run_id_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _compact_rows(rows: list[dict[str, Any]], sample_size: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows[:sample_size]:
        out.append(
            {
                "url": row.get("url"),
                "title_raw": row.get("title_raw"),
                "normalized_title": row.get("normalized_title"),
                "role_family": row.get("role_family"),
                "location_type": row.get("location_type"),
                "has_salary": row.get("has_salary"),
                "has_skills": row.get("has_skills"),
                "published_at": row.get("published_at"),
            }
        )
    return out


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _try_acquire_lock(lock_path: Path) -> bool:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(str(lock_path), flags)
    except FileExistsError:
        return False
    try:
        payload = {
            "pid": os.getpid(),
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        os.write(fd, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    finally:
        os.close(fd)
    return True


def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass


def run_enabled_saved_searches(
    *,
    saved_db_path: str | Path = "data/jobs/saved_searches.db",
    indexed_input_path: str | Path = "data/jobs/jobs_indexed_en.jsonl",
    indexed_sqlite_path: str | Path | None = None,
    outdir: str | Path = "data/alerts/runs",
    scan_limit: int = 5000,
    return_limit: int = 200,
    sample_size: int = 5,
    user_id: str = "local-user",
    user_email: str | None = None,
) -> dict[str, Any]:
    run_id = _run_id_now()
    run_ts = datetime.now(timezone.utc).isoformat()

    searches = list_saved_searches(db_path=saved_db_path, user_id=user_id)
    enabled = [
        s
        for s in searches
        if bool(s.get("is_enabled")) and str(s.get("lifecycle") or "active").strip().lower() == "active"
    ]

    results: list[dict[str, Any]] = []
    total_new = 0
    for s in enabled:
        try:
            rep = check_new_matches(
                db_path=saved_db_path,
                search_id=s["search_id"],
                indexed_input_path=indexed_input_path,
                indexed_sqlite_path=indexed_sqlite_path,
                scan_limit=scan_limit,
                return_limit=return_limit,
                offset=0,
                user_id=user_id,
            )
            item = {
                "search_id": s["search_id"],
                "name": s["name"],
                "query_type": s["query_type"],
                "enabled": True,
                "run_timestamp": run_ts,
                "total_current_matches": rep["current_count"],
                "new_matches_count": rep["new_count"],
                "sample_new_matches": _compact_rows(rep["new_results"], sample_size=sample_size),
                "status": "ok",
            }
            total_new += int(rep["new_count"])
        except Exception as exc:  # pragma: no cover - defensive
            item = {
                "search_id": s["search_id"],
                "name": s.get("name"),
                "query_type": s.get("query_type"),
                "enabled": True,
                "run_timestamp": run_ts,
                "total_current_matches": None,
                "new_matches_count": None,
                "sample_new_matches": [],
                "status": "error",
                "error": str(exc),
            }
        results.append(item)

    report = {
        "run_id": run_id,
        "run_timestamp": run_ts,
        "saved_db_path": str(saved_db_path),
        "user_id": user_id,
        "user_email": user_email,
        "indexed_input_path": str(indexed_input_path),
        "indexed_sqlite_path": None if indexed_sqlite_path is None else str(indexed_sqlite_path),
        "searches_total": len(searches),
        "searches_enabled": len(enabled),
        "searches_disabled": len(searches) - len(enabled),
        "processed_ok": sum(1 for x in results if x.get("status") == "ok"),
        "processed_error": sum(1 for x in results if x.get("status") == "error"),
        "total_new_matches": total_new,
        "results": results,
    }

    out_path = per_user_runs_dir(runs_dir=outdir, user_id=user_id)
    out_path.mkdir(parents=True, exist_ok=True)
    json_file = out_path / f"{run_id}.json"
    md_file = out_path / f"{run_id}.md"
    json_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        f"# Saved Search Runner {run_id}",
        "",
        f"- run_timestamp: {run_ts}",
        f"- searches_total: {report['searches_total']}",
        f"- searches_enabled: {report['searches_enabled']}",
        f"- searches_disabled: {report['searches_disabled']}",
        f"- processed_ok: {report['processed_ok']}",
        f"- processed_error: {report['processed_error']}",
        f"- total_new_matches: {report['total_new_matches']}",
        "",
        "## Results",
    ]
    for r in results:
        md_lines.append(f"### {r['name']} ({r['search_id']})")
        md_lines.append(f"- query_type: {r['query_type']}")
        md_lines.append(f"- status: {r['status']}")
        md_lines.append(f"- total_current_matches: {r['total_current_matches']}")
        md_lines.append(f"- new_matches_count: {r['new_matches_count']}")
        if r["sample_new_matches"]:
            md_lines.append(f"- sample_new_matches ({len(r['sample_new_matches'])}):")
            for row in r["sample_new_matches"]:
                md_lines.append(
                    f"  - {row['url']} | {row['title_raw']} | {row['normalized_title']} | family={row['role_family']}"
                )
        md_lines.append("")
    md_file.write_text("\n".join(md_lines), encoding="utf-8")

    report["json_report_path"] = str(json_file)
    report["md_report_path"] = str(md_file)
    return report


def run_due_saved_searches(
    *,
    saved_db_path: str | Path = "data/jobs/saved_searches.db",
    indexed_input_path: str | Path = "data/jobs/jobs_indexed_en.jsonl",
    indexed_sqlite_path: str | Path | None = None,
    outdir: str | Path = "data/alerts/runs",
    scan_limit: int = 5000,
    return_limit: int = 200,
    sample_size: int = 5,
    user_id: str = "local-user",
    user_email: str | None = None,
) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    started_iso = started.isoformat()
    run_id = _run_id_now()
    run_ts = datetime.now(timezone.utc).isoformat()
    now = datetime.now(timezone.utc)
    out_path = per_user_runs_dir(runs_dir=outdir, user_id=user_id)
    lock_path = out_path / ".run_due.lock"
    lock_acquired = _try_acquire_lock(lock_path)
    if not lock_acquired:
        finished = datetime.now(timezone.utc)
        return {
            "run_id": run_id,
            "run_timestamp": run_ts,
            "started_at": started_iso,
            "finished_at": finished.isoformat(),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "saved_db_path": str(saved_db_path),
            "user_id": user_id,
            "user_email": user_email,
            "indexed_input_path": str(indexed_input_path),
            "indexed_sqlite_path": None if indexed_sqlite_path is None else str(indexed_sqlite_path),
            "run_scope": "due_only",
            "lock_acquired": False,
            "lock_path": str(lock_path),
            "status": "skipped_locked",
            "searches_total": 0,
            "searches_due": 0,
            "searches_skipped_not_due": 0,
            "processed_ok": 0,
            "processed_error": 0,
            "total_new_matches": 0,
            "results": [],
            "json_report_path": None,
            "md_report_path": None,
        }

    try:
        searches = list_saved_searches(db_path=saved_db_path, user_id=user_id)
        due = [s for s in searches if is_saved_search_due(s, now=now)]

        results: list[dict[str, Any]] = []
        total_new = 0
        for s in due:
            try:
                rep = check_new_matches(
                    db_path=saved_db_path,
                    search_id=s["search_id"],
                    indexed_input_path=indexed_input_path,
                    indexed_sqlite_path=indexed_sqlite_path,
                    scan_limit=scan_limit,
                    return_limit=return_limit,
                    offset=0,
                    user_id=user_id,
                )
                item = {
                    "search_id": s["search_id"],
                    "name": s["name"],
                    "query_type": s["query_type"],
                    "frequency": s.get("frequency", "daily"),
                    "enabled": True,
                    "run_timestamp": run_ts,
                    "total_current_matches": rep["current_count"],
                    "new_matches_count": rep["new_count"],
                    "sample_new_matches": _compact_rows(rep["new_results"], sample_size=sample_size),
                    "status": "ok",
                }
                total_new += int(rep["new_count"])
            except Exception as exc:  # pragma: no cover - defensive
                item = {
                    "search_id": s["search_id"],
                    "name": s.get("name"),
                    "query_type": s.get("query_type"),
                    "frequency": s.get("frequency", "daily"),
                    "enabled": True,
                    "run_timestamp": run_ts,
                    "total_current_matches": None,
                    "new_matches_count": None,
                    "sample_new_matches": [],
                    "status": "error",
                    "error": str(exc),
                }
            results.append(item)

        finished = datetime.now(timezone.utc)
        report = {
            "run_id": run_id,
            "run_timestamp": run_ts,
            "started_at": started_iso,
            "finished_at": finished.isoformat(),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "saved_db_path": str(saved_db_path),
            "user_id": user_id,
            "user_email": user_email,
            "indexed_input_path": str(indexed_input_path),
            "indexed_sqlite_path": None if indexed_sqlite_path is None else str(indexed_sqlite_path),
            "run_scope": "due_only",
            "lock_acquired": True,
            "lock_path": str(lock_path),
            "status": "ok",
            "searches_total": len(searches),
            "searches_due": len(due),
            "searches_skipped_not_due": len(searches) - len(due),
            "processed_ok": sum(1 for x in results if x.get("status") == "ok"),
            "processed_error": sum(1 for x in results if x.get("status") == "error"),
            "total_new_matches": total_new,
            "results": results,
        }

        out_path.mkdir(parents=True, exist_ok=True)
        json_file = out_path / f"{run_id}.json"
        md_file = out_path / f"{run_id}.md"
        _write_text_atomic(json_file, json.dumps(report, ensure_ascii=False, indent=2))

        md_lines = [
            f"# Saved Search Runner Due {run_id}",
            "",
            f"- run_timestamp: {run_ts}",
            f"- started_at: {report['started_at']}",
            f"- finished_at: {report['finished_at']}",
            f"- duration_seconds: {report['duration_seconds']}",
            f"- run_scope: due_only",
            f"- lock_acquired: {report['lock_acquired']}",
            f"- lock_path: {report['lock_path']}",
            f"- searches_total: {report['searches_total']}",
            f"- searches_due: {report['searches_due']}",
            f"- searches_skipped_not_due: {report['searches_skipped_not_due']}",
            f"- processed_ok: {report['processed_ok']}",
            f"- processed_error: {report['processed_error']}",
            f"- total_new_matches: {report['total_new_matches']}",
            "",
            "## Results",
        ]
        for r in results:
            md_lines.append(f"### {r['name']} ({r['search_id']})")
            md_lines.append(f"- query_type: {r['query_type']}")
            md_lines.append(f"- frequency: {r.get('frequency')}")
            md_lines.append(f"- status: {r['status']}")
            md_lines.append(f"- total_current_matches: {r['total_current_matches']}")
            md_lines.append(f"- new_matches_count: {r['new_matches_count']}")
            if r["sample_new_matches"]:
                md_lines.append(f"- sample_new_matches ({len(r['sample_new_matches'])}):")
                for row in r["sample_new_matches"]:
                    md_lines.append(
                        f"  - {row['url']} | {row['title_raw']} | {row['normalized_title']} | family={row['role_family']}"
                    )
            md_lines.append("")
        _write_text_atomic(md_file, "\n".join(md_lines))

        report["json_report_path"] = str(json_file)
        report["md_report_path"] = str(md_file)
        return report
    finally:
        _release_lock(lock_path)
