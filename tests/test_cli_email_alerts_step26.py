from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_alerts_send_email_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "alerts",
            "send-email",
            "--run-json",
            "data/alerts/runs/x.json",
            "--to",
            "to@example.com",
            "--smtp-host",
            "smtp.example.com",
            "--from-email",
            "from@example.com",
        ]
    )
    assert args.group == "alerts"
    assert args.alerts_cmd == "send-email"
    assert args.smtp_port == 587


def test_cli_alerts_send_email_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_send_email_alerts_from_run(*, run_json_path, to_email, smtp_config):
        called["run_json_path"] = str(run_json_path)
        called["to_email"] = to_email
        called["smtp_host"] = smtp_config.host
        return {"sent_count": 1, "skipped_zero_count": 0, "error_count": 0, "errors": []}

    monkeypatch.setattr(cli, "send_email_alerts_from_run", _fake_send_email_alerts_from_run)
    rc = cli._cmd_alerts_send_email(
        type(
            "Args",
            (),
            {
                "run_json": str(tmp_path / "run.json"),
                "to": "to@example.com",
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "smtp_user": "user",
                "smtp_password": "pass",
                "from_email": "from@example.com",
                "no_tls": False,
            },
        )
    )
    assert rc == 0
    assert called["to_email"] == "to@example.com"
    assert called["smtp_host"] == "smtp.example.com"
