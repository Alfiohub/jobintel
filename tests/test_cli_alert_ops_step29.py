from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_alerts_cleanup_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "alerts",
            "cleanup",
            "--outdir",
            "data/alerts/runs",
            "--keep-last",
            "10",
        ]
    )
    assert args.group == "alerts"
    assert args.alerts_cmd == "cleanup"
    assert args.keep_last == 10


def test_cli_alerts_cleanup_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_cleanup_alert_runs(*, runs_dir, keep_last):
        called["runs_dir"] = str(runs_dir)
        called["keep_last"] = keep_last
        return {"removed_runs_count": 1}

    monkeypatch.setattr(cli, "cleanup_alert_runs", _fake_cleanup_alert_runs)
    rc = cli._cmd_alerts_cleanup(
        type(
            "Args",
            (),
            {
                "outdir": str(tmp_path / "alerts" / "runs"),
                "keep_last": 7,
            },
        )
    )
    assert rc == 0
    assert called["keep_last"] == 7
