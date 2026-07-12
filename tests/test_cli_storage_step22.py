from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_storage_build_index_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "storage",
            "build-index",
            "--input",
            "data/jobs/jobs_indexed_en.jsonl",
            "--sqlite",
            "data/jobs/jobs_indexed_en.db",
        ]
    )
    assert args.group == "storage"
    assert args.storage_cmd == "build-index"
    assert args.sqlite.endswith(".db")


def test_cli_storage_build_index_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_build_sqlite_index(*, input_path, sqlite_path, batch_size):
        called["input_path"] = str(input_path)
        called["sqlite_path"] = str(sqlite_path)
        called["batch_size"] = batch_size
        return {
            "input_path": str(input_path),
            "sqlite_path": str(sqlite_path),
            "rows_total": 3,
            "invalid_rows": 0,
            "inserted_rows": 3,
        }

    monkeypatch.setattr(cli, "build_sqlite_index", _fake_build_sqlite_index)
    rc = cli._cmd_storage_build_index(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "in.jsonl"),
                "sqlite": str(tmp_path / "jobs.db"),
                "batch_size": 500,
            },
        )
    )
    assert rc == 0
    assert called["batch_size"] == 500
