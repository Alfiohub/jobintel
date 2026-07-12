from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_serve_query_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "serve",
            "query",
            "--input",
            "data/jobs/jobs_indexed_en.jsonl",
            "--normalized-title",
            "account_executive",
            "--limit",
            "20",
            "--offset",
            "10",
        ]
    )
    assert args.group == "serve"
    assert args.serve_cmd == "query"
    assert args.normalized_title == "account_executive"
    assert args.limit == 20
    assert args.offset == 10


def test_cli_serve_query_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_list_jobs(*, input_path, query, limit, offset, sqlite_path=None):
        called["input_path"] = str(input_path)
        called["query"] = query
        called["limit"] = limit
        called["offset"] = offset
        called["sqlite_path"] = sqlite_path
        return {"results": [], "total_count": 1, "returned_count": 0}

    monkeypatch.setattr(cli, "list_jobs", _fake_list_jobs)
    rc = cli._cmd_serve_query(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "idx.jsonl"),
                "sqlite": None,
                "out": str(tmp_path / "out.jsonl"),
                "normalized_title": "account_executive",
                "role_family": None,
                "language_bucket": None,
                "location_type": None,
                "employment_type": None,
                "has_salary": None,
                "has_skills": None,
                "title_is_other": None,
                "skills_contains": None,
                "salary_currency": None,
                "sort_by": "published_at_desc",
                "limit": 10,
                "offset": 5,
            },
        )
    )
    assert rc == 0
    assert called["input_path"] == str(tmp_path / "idx.jsonl")
    assert called["query"].normalized_title == "account_executive"
    assert called["limit"] == 10
    assert called["offset"] == 5


def test_cli_serve_pack_count_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_count_pack(*, input_path, pack_name, sqlite_path=None):
        called["input_path"] = str(input_path)
        called["pack_name"] = pack_name
        called["sqlite_path"] = sqlite_path
        return {"count": 42}

    monkeypatch.setattr(cli, "count_pack", _fake_count_pack)
    rc = cli._cmd_serve_pack_count(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "idx.jsonl"),
                "sqlite": None,
                "pack": "python_tech_jobs",
            },
        )
    )
    assert rc == 0
    assert called["input_path"] == str(tmp_path / "idx.jsonl")
    assert called["pack_name"] == "python_tech_jobs"
