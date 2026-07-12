from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


def normalize_user_id(user_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", user_id.strip())
    return cleaned or "local-user"


def per_user_runs_dir(*, runs_dir: str | Path, user_id: str) -> Path:
    return Path(runs_dir) / normalize_user_id(user_id)


def _json_run_files_sorted(runs_dir: str | Path) -> list[Path]:
    base = Path(runs_dir)
    if not base.exists() or not base.is_dir():
        return []
    return sorted(base.glob("*.json"), key=lambda x: x.name, reverse=True)


def list_alert_runs(*, runs_dir: str | Path, user_id: str | None = None) -> list[dict[str, Any]]:
    base = per_user_runs_dir(runs_dir=runs_dir, user_id=user_id) if user_id else Path(runs_dir)
    out: list[dict[str, Any]] = []
    for p in _json_run_files_sorted(base):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        run_id = str(obj.get("run_id") or p.stem)
        out.append(
            {
                "run_id": run_id,
                "run_timestamp": obj.get("run_timestamp"),
                "user_id": obj.get("user_id"),
                "searches_total": obj.get("searches_total"),
                "searches_enabled": obj.get("searches_enabled"),
                "processed_ok": obj.get("processed_ok"),
                "processed_error": obj.get("processed_error"),
                "total_new_matches": obj.get("total_new_matches"),
                "email_delivery": obj.get("email_delivery"),
                "digest_delivery": obj.get("digest_delivery"),
                "json_report_path": str(p),
                "md_report_path": str(base / f"{run_id}.md"),
            }
        )
    return out


def get_alert_run_detail(*, runs_dir: str | Path, run_id: str, user_id: str | None = None) -> dict[str, Any]:
    base = per_user_runs_dir(runs_dir=runs_dir, user_id=user_id) if user_id else Path(runs_dir)
    p = base / f"{run_id}.json"
    if not p.exists() or not p.is_file():
        raise ValueError(f"alert run not found: {run_id}")
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"invalid alert run artifact: {run_id}")
    if user_id is not None and str(obj.get("user_id") or "") != user_id:
        # Defensive check in case artifacts are moved/copied manually.
        raise ValueError(f"alert run not found: {run_id}")
    obj.setdefault("json_report_path", str(p))
    md_path = base / f"{run_id}.md"
    obj.setdefault("md_report_path", str(md_path))
    return obj


def get_alert_runs_summary(
    *,
    runs_dir: str | Path,
    user_id: str | None = None,
    recent_limit: int = 20,
    sample_new_searches: int = 5,
) -> dict[str, Any]:
    runs = list_alert_runs(runs_dir=runs_dir, user_id=user_id)
    recent = runs[:recent_limit]
    latest = recent[0] if recent else None
    recent_error_runs_count = 0
    recent_ok_runs_count = 0
    recent_searches_with_new_matches: list[dict[str, Any]] = []

    for run in recent:
        try:
            detail = get_alert_run_detail(runs_dir=runs_dir, run_id=run["run_id"], user_id=user_id)
        except ValueError:
            continue
        if int(detail.get("processed_error") or 0) > 0:
            recent_error_runs_count += 1
        if int(detail.get("processed_ok") or 0) > 0:
            recent_ok_runs_count += 1

        for item in detail.get("results", []):
            if not isinstance(item, dict):
                continue
            new_count = int(item.get("new_matches_count") or 0)
            if new_count <= 0:
                continue
            recent_searches_with_new_matches.append(
                {
                    "run_id": detail.get("run_id"),
                    "search_id": item.get("search_id"),
                    "name": item.get("name"),
                    "new_matches_count": new_count,
                    "query_type": item.get("query_type"),
                }
            )
            if len(recent_searches_with_new_matches) >= sample_new_searches:
                break
        if len(recent_searches_with_new_matches) >= sample_new_searches:
            break

    return {
        "runs_count": len(runs),
        "latest_run_id": None if latest is None else latest.get("run_id"),
        "latest_run_total_new_matches": None if latest is None else latest.get("total_new_matches"),
        "recent_error_runs_count": recent_error_runs_count,
        "recent_ok_runs_count": recent_ok_runs_count,
        "recent_searches_with_new_matches": recent_searches_with_new_matches,
    }


def cleanup_alert_runs(*, runs_dir: str | Path, keep_last: int = 20) -> dict[str, Any]:
    if keep_last < 0:
        raise ValueError("keep_last must be >= 0")
    files = _json_run_files_sorted(runs_dir)
    to_keep = {p.stem for p in files[:keep_last]}
    removed_json: list[str] = []
    removed_md: list[str] = []
    for p in files[keep_last:]:
        try:
            p.unlink(missing_ok=True)
            removed_json.append(str(p))
        except Exception:
            pass
        md = p.with_suffix(".md")
        try:
            md.unlink(missing_ok=True)
            removed_md.append(str(md))
        except Exception:
            pass
    return {
        "runs_dir": str(runs_dir),
        "keep_last": keep_last,
        "kept_runs_count": min(len(files), keep_last),
        "removed_runs_count": len(removed_json),
        "removed_json_files": removed_json,
        "removed_md_files": removed_md,
        "remaining_runs_count": len(files) - len(removed_json),
        "kept_run_ids": sorted(to_keep, reverse=True),
    }
