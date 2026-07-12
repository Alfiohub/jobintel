from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import smtplib
from typing import Any

from email.message import EmailMessage


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    from_email: str
    user: str | None = None
    password: str | None = None
    use_tls: bool = True

    @staticmethod
    def from_env() -> "SMTPConfig":
        host = os.getenv("JOBINTEL_SMTP_HOST", "")
        from_email = os.getenv("JOBINTEL_SMTP_FROM", "")
        if not host or not from_email:
            raise ValueError("missing SMTP env config: JOBINTEL_SMTP_HOST and JOBINTEL_SMTP_FROM are required")
        port_raw = os.getenv("JOBINTEL_SMTP_PORT", "587")
        return SMTPConfig(
            host=host,
            port=int(port_raw),
            from_email=from_email,
            user=os.getenv("JOBINTEL_SMTP_USER") or None,
            password=os.getenv("JOBINTEL_SMTP_PASSWORD") or None,
            use_tls=os.getenv("JOBINTEL_SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes"},
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_email_subject(*, search_name: str, new_matches_count: int) -> str:
    suffix = "match" if new_matches_count == 1 else "matches"
    return f"[JobIntel] {new_matches_count} new {suffix} · {search_name}"


def build_email_body_text(
    *,
    search_name: str,
    new_matches_count: int,
    run_timestamp: str,
    sample_new_matches: list[dict[str, Any]],
) -> str:
    lines = [
        "JobIntel Alert",
        "",
        f"Saved search: {search_name}",
        f"New matches: {new_matches_count}",
        f"Run timestamp: {run_timestamp}",
        "",
        "Sample new matches:",
    ]
    if not sample_new_matches:
        lines.append("- (no sample rows)")
    else:
        for row in sample_new_matches:
            title = str(row.get("title_raw") or "(no title)")
            url = str(row.get("url") or "")
            lines.append(f"- {title}")
            lines.append(f"  {url}")
    return "\n".join(lines)


def build_email_body_html(
    *,
    search_name: str,
    new_matches_count: int,
    run_timestamp: str,
    sample_new_matches: list[dict[str, Any]],
) -> str:
    rows: list[str] = []
    for row in sample_new_matches:
        title = escape(str(row.get("title_raw") or "(no title)"))
        url = escape(str(row.get("url") or ""))
        rows.append(f"<li><strong>{title}</strong><br><a href=\"{url}\">{url}</a></li>")
    rows_html = "\n".join(rows) if rows else "<li>(no sample rows)</li>"
    return (
        "<html><body>"
        "<h3>JobIntel Alert</h3>"
        f"<p><strong>Saved search:</strong> {escape(search_name)}<br>"
        f"<strong>New matches:</strong> {new_matches_count}<br>"
        f"<strong>Run timestamp:</strong> {escape(run_timestamp)}</p>"
        "<p><strong>Sample new matches:</strong></p>"
        f"<ul>{rows_html}</ul>"
        "</body></html>"
    )


def send_email_message(
    *,
    smtp: SMTPConfig,
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> None:
    msg = EmailMessage()
    msg["From"] = smtp.from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

    with smtplib.SMTP(smtp.host, smtp.port, timeout=20) as server:
        if smtp.use_tls:
            server.starttls()
        if smtp.user:
            server.login(smtp.user, smtp.password or "")
        server.send_message(msg)


def send_email_alerts_from_run(
    *,
    run_json_path: str | Path,
    to_email: str,
    smtp_config: SMTPConfig,
) -> dict[str, Any]:
    attempted_at = _now_iso()
    path = Path(run_json_path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("run report JSON must be an object")
    results = obj.get("results")
    if not isinstance(results, list):
        raise ValueError("run report JSON missing results list")

    sent = 0
    attempted = 0
    skipped_zero = 0
    skipped_status = 0
    errors: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "ok":
            skipped_status += 1
            continue
        count = int(item.get("new_matches_count") or 0)
        if count <= 0:
            skipped_zero += 1
            continue
        attempted += 1
        search_name = str(item.get("name") or "saved search")
        run_ts = str(item.get("run_timestamp") or obj.get("run_timestamp") or "")
        sample = item.get("sample_new_matches")
        sample_rows = sample if isinstance(sample, list) else []
        subject = build_email_subject(search_name=search_name, new_matches_count=count)
        body_text = build_email_body_text(
            search_name=search_name,
            new_matches_count=count,
            run_timestamp=run_ts,
            sample_new_matches=sample_rows,
        )
        body_html = build_email_body_html(
            search_name=search_name,
            new_matches_count=count,
            run_timestamp=run_ts,
            sample_new_matches=sample_rows,
        )
        try:
            send_email_message(
                smtp=smtp_config,
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
            )
            sent += 1
        except Exception as exc:  # pragma: no cover - defensive
            errors.append({"search_id": item.get("search_id"), "name": search_name, "error": str(exc)})

    skipped = skipped_zero + skipped_status
    return {
        "run_json_path": str(path),
        "attempted_at": attempted_at,
        "delivery_timestamp": _now_iso(),
        "to_email": to_email,
        "attempted_count": attempted,
        "sent_count": sent,
        "skipped_zero_count": skipped_zero,
        "skipped_status_count": skipped_status,
        "skipped_count": skipped,
        "error_count": len(errors),
        "email_attempted": attempted > 0,
        "email_sent": sent > 0,
        "email_skipped": skipped,
        "email_error": len(errors) > 0,
        "errors": errors,
    }


def persist_email_delivery_to_run(
    *,
    run_json_path: str | Path,
    email_delivery: dict[str, Any],
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
    obj["email_delivery"] = email_delivery
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
