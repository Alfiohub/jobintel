from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_saved_search_create_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "saved-search",
            "create",
            "--name",
            "my search",
            "--query-type",
            "pack",
            "--pack-name",
            "account_executive_jobs",
        ]
    )
    assert args.group == "saved-search"
    assert args.saved_cmd == "create"
    assert args.query_type == "pack"


def test_cli_saved_search_run_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_saved_search(
        *,
        db_path,
        search_id,
        indexed_input_path,
        indexed_sqlite_path=None,
        limit=100,
        offset=0,
    ):
        called["db_path"] = str(db_path)
        called["search_id"] = search_id
        called["indexed_input_path"] = str(indexed_input_path)
        called["indexed_sqlite_path"] = None if indexed_sqlite_path is None else str(indexed_sqlite_path)
        called["limit"] = limit
        called["offset"] = offset
        return {"ok": True}

    monkeypatch.setattr(cli, "run_saved_search", _fake_run_saved_search)
    rc = cli._cmd_saved_search_run(
        type(
            "Args",
            (),
            {
                "saved_db": str(tmp_path / "saved.db"),
                "id": "abc",
                "input": str(tmp_path / "jobs.jsonl"),
                "sqlite": str(tmp_path / "jobs.db"),
                "limit": 50,
                "offset": 3,
            },
        )
    )
    assert rc == 0
    assert called["search_id"] == "abc"
    assert called["limit"] == 50
    assert called["offset"] == 3
