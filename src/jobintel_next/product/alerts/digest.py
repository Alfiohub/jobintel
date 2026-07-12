from __future__ import annotations

from html import escape
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .email import SMTPConfig, send_email_message


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_digest_subject(
    *,
    total_new_matches: int,
    searches_with_new_matches: int,
) -> str:
    return (
        f"[JobIntel] Daily digest · {total_new_matches} new matches "
        f"across {searches_with_new_matches} searches"
    )


def _searches_with_new(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "") != "ok":
            continue
        if int(item.get("new_matches_count") or 0) <= 0:
            continue
        out.append(item)
    return out


def build_digest_body_text(
    *,
    run_timestamp: str,
    searches_total: int,
    searches_processed: int,
    searches_with_new_matches: int,
    total_new_matches: int,
    results: list[dict[str, Any]],
    attention_items: list[dict[str, Any]] | None = None,
) -> str:
    lines = [
        "JobIntel Daily Digest",
        "",
        f"Run timestamp: {run_timestamp}",
        f"Saved searches total: {searches_total}",
        f"Saved searches processed: {searches_processed}",
        f"Searches with new matches: {searches_with_new_matches}",
        f"Total new matches: {total_new_matches}",
        "",
    ]
    if searches_with_new_matches <= 0:
        lines.append("No new matches in this run.")
        return "\n".join(lines)

    lines.append("Saved searches with new matches:")
    for item in _searches_with_new(results):
        name = str(item.get("name") or "saved search")
        count = int(item.get("new_matches_count") or 0)
        lines.append("")
        lines.append(f"- {name}: {count} new")
        sample = item.get("sample_new_matches")
        rows = sample if isinstance(sample, list) else []
        if not rows:
            lines.append("  (no sample rows)")
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title_raw") or "(no title)")
            url = str(row.get("url") or "")
            lines.append(f"  - {title}")
            lines.append(f"    {url}")
    attention = [x for x in (attention_items or []) if isinstance(x, dict)]
    if attention:
        lines.append("")
        lines.append("Needs attention:")
        for item in attention[:5]:
            lines.append(f"- [{str(item.get('priority') or 'low')}] {str(item.get('title') or '-')}")
            href = str(item.get("href") or "").strip()
            if href:
                lines.append(f"  {href}")
    return "\n".join(lines)


def build_digest_body_html(
    *,
    run_timestamp: str,
    searches_total: int,
    searches_processed: int,
    searches_with_new_matches: int,
    total_new_matches: int,
    results: list[dict[str, Any]],
    attention_items: list[dict[str, Any]] | None = None,
) -> str:
    blocks: list[str] = []
    for item in _searches_with_new(results):
        name = escape(str(item.get("name") or "saved search"))
        count = int(item.get("new_matches_count") or 0)
        rows_html: list[str] = []
        sample = item.get("sample_new_matches")
        rows = sample if isinstance(sample, list) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = escape(str(row.get("title_raw") or "(no title)"))
            url = escape(str(row.get("url") or ""))
            rows_html.append(f"<li><strong>{title}</strong><br><a href=\"{url}\">{url}</a></li>")
        rows_block = "<ul>" + ("".join(rows_html) if rows_html else "<li>(no sample rows)</li>") + "</ul>"
        blocks.append(f"<h4>{name} · {count} new</h4>{rows_block}")

    content = "".join(blocks) if blocks else "<p>No new matches in this run.</p>"
    attention = [x for x in (attention_items or []) if isinstance(x, dict)]
    attention_html = ""
    if attention:
        rows = []
        for item in attention[:5]:
            priority = escape(str(item.get("priority") or "low"))
            title = escape(str(item.get("title") or "-"))
            href = escape(str(item.get("href") or ""))
            link_html = f'<a href="{href}">{href}</a>' if href else ""
            rows.append(f"<li><strong>[{priority}]</strong> {title}<br>{link_html}</li>")
        attention_html = "<h4>Needs attention</h4><ul>" + "".join(rows) + "</ul>"
    return (
        "<html><body>"
        "<h3>JobIntel Daily Digest</h3>"
        f"<p><strong>Run timestamp:</strong> {escape(run_timestamp)}<br>"
        f"<strong>Saved searches total:</strong> {searches_total}<br>"
        f"<strong>Saved searches processed:</strong> {searches_processed}<br>"
        f"<strong>Searches with new matches:</strong> {searches_with_new_matches}<br>"
        f"<strong>Total new matches:</strong> {total_new_matches}</p>"
        f"{content}"
        f"{attention_html}"
        "</body></html>"
    )


def send_digest_email_from_run(
    *,
    run_json_path: str | Path,
    to_email: str,
    smtp_config: SMTPConfig,
    attention_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    attempted_at = _now_iso()
    path = Path(run_json_path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("run report JSON must be an object")
    results_raw = obj.get("results")
    if not isinstance(results_raw, list):
        raise ValueError("run report JSON missing results list")
    results = [x for x in results_raw if isinstance(x, dict)]

    processed = int(obj.get("processed_ok") or 0)
    searches_total = int(obj.get("searches_total") or 0)
    searches_with_new = len(_searches_with_new(results))
    total_new_matches = int(obj.get("total_new_matches") or 0)
    run_timestamp = str(obj.get("run_timestamp") or "")

    if total_new_matches <= 0 or searches_with_new <= 0:
        return {
            "run_json_path": str(path),
            "attempted_at": attempted_at,
            "delivery_timestamp": attempted_at,
            "to_email": to_email,
            "attempted_count": 0,
            "sent_count": 0,
            "skipped_count": 1,
            "skip_reason": "no_new_matches",
            "error_count": 0,
            "email_attempted": False,
            "email_sent": False,
            "email_skipped": 1,
            "email_error": False,
            "errors": [],
            "attention_items_count": len([x for x in (attention_items or []) if isinstance(x, dict)]),
            "total_new_matches": total_new_matches,
            "searches_with_new_matches": searches_with_new,
        }

    subject = build_digest_subject(
        total_new_matches=total_new_matches,
        searches_with_new_matches=searches_with_new,
    )
    body_text = build_digest_body_text(
        run_timestamp=run_timestamp,
        searches_total=searches_total,
        searches_processed=processed,
        searches_with_new_matches=searches_with_new,
        total_new_matches=total_new_matches,
        results=results,
        attention_items=attention_items,
    )
    body_html = build_digest_body_html(
        run_timestamp=run_timestamp,
        searches_total=searches_total,
        searches_processed=processed,
        searches_with_new_matches=searches_with_new,
        total_new_matches=total_new_matches,
        results=results,
        attention_items=attention_items,
    )

    try:
        send_email_message(
            smtp=smtp_config,
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "run_json_path": str(path),
            "attempted_at": attempted_at,
            "delivery_timestamp": _now_iso(),
            "to_email": to_email,
            "attempted_count": 1,
            "sent_count": 0,
            "skipped_count": 0,
            "error_count": 1,
            "email_attempted": True,
            "email_sent": False,
            "email_skipped": 0,
            "email_error": True,
            "errors": [{"error": str(exc)}],
            "attention_items_count": len([x for x in (attention_items or []) if isinstance(x, dict)]),
            "total_new_matches": total_new_matches,
            "searches_with_new_matches": searches_with_new,
        }

    return {
        "run_json_path": str(path),
        "attempted_at": attempted_at,
        "delivery_timestamp": _now_iso(),
        "to_email": to_email,
        "attempted_count": 1,
        "sent_count": 1,
        "skipped_count": 0,
        "error_count": 0,
        "email_attempted": True,
        "email_sent": True,
        "email_skipped": 0,
        "email_error": False,
        "errors": [],
        "attention_items_count": len([x for x in (attention_items or []) if isinstance(x, dict)]),
        "total_new_matches": total_new_matches,
        "searches_with_new_matches": searches_with_new,
    }


def resend_digest_from_run_artifact(
    *,
    run_json_path: str | Path,
    smtp_config: SMTPConfig,
    to_email: str | None = None,
) -> dict[str, Any]:
    path = Path(run_json_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"run artifact not found: {path}")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("run report JSON must be an object")

    destination = (to_email or "").strip() or None
    if destination is None:
        digest_meta = obj.get("digest_delivery")
        if isinstance(digest_meta, dict):
            destination = str(digest_meta.get("to_email") or "").strip() or None
    if destination is None:
        raise ValueError("missing destination email: pass --to or ensure digest_delivery.to_email is present in run artifact")

    delivery = send_digest_email_from_run(
        run_json_path=path,
        to_email=destination,
        smtp_config=smtp_config,
    )
    delivery["resend"] = True
    delivery["resend_of_run_id"] = str(obj.get("run_id") or path.stem)
    persist_digest_delivery_to_run(run_json_path=path, digest_delivery=delivery)
    return delivery


def persist_digest_delivery_to_run(
    *,
    run_json_path: str | Path,
    digest_delivery: dict[str, Any],
) -> None:
    path = Path(run_json_path)
    if not path.exists() or not path.is_file():
        return
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(obj, dict):
        return
    obj["digest_delivery"] = digest_delivery
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
