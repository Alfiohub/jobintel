from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_saved_search_run_all_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "saved-search",
            "run-all",
            "--saved-db",
            "data/jobs/saved_searches.db",
            "--input",
            "data/jobs/jobs_indexed_en.jsonl",
            "--outdir",
            "data/alerts/runs",
        ]
    )
    assert args.group == "saved-search"
    assert args.saved_cmd == "run-all"


def test_cli_saved_search_run_all_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_runner(
        *,
        saved_db_path,
        indexed_input_path,
        indexed_sqlite_path=None,
        outdir,
        scan_limit=5000,
        return_limit=200,
        sample_size=5,
    ):
        called["saved_db_path"] = str(saved_db_path)
        called["indexed_input_path"] = str(indexed_input_path)
        called["indexed_sqlite_path"] = None if indexed_sqlite_path is None else str(indexed_sqlite_path)
        called["outdir"] = str(outdir)
        called["scan_limit"] = scan_limit
        called["return_limit"] = return_limit
        called["sample_size"] = sample_size
        return {
            "run_id": "rid",
            "searches_enabled": 2,
            "processed_ok": 2,
            "processed_error": 0,
            "total_new_matches": 3,
            "json_report_path": str(Path(outdir) / "rid.json"),
            "md_report_path": str(Path(outdir) / "rid.md"),
        }

    monkeypatch.setattr(cli, "run_enabled_saved_searches", _fake_runner)
    rc = cli._cmd_saved_search_run_all(
        type(
            "Args",
            (),
            {
                "saved_db": str(tmp_path / "saved.db"),
                "input": str(tmp_path / "jobs.jsonl"),
                "sqlite": str(tmp_path / "jobs.db"),
                "outdir": str(tmp_path / "alerts"),
                "scan_limit": 999,
                "limit": 111,
                "sample_size": 7,
            },
        )
    )
    assert rc == 0
    assert called["scan_limit"] == 999
    assert called["return_limit"] == 111
    assert called["sample_size"] == 7
