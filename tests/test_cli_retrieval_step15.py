from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_retrieval_query_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "retrieval",
            "query",
            "--input",
            "data/jobs/jobs_indexed_en.jsonl",
            "--normalized-title",
            "data_engineer",
            "--has-salary",
            "true",
            "--skills-contains",
            "python",
            "--sort-by",
            "published_at_desc",
            "--limit",
            "20",
        ]
    )
    assert args.group == "retrieval"
    assert args.retrieval_cmd == "query"
    assert args.normalized_title == "data_engineer"
    assert args.limit == 20


def test_cli_retrieval_query_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_retrieval_query(*, input_path, query, output_path=None):
        called["input_path"] = str(input_path)
        called["query"] = query
        called["output_path"] = None if output_path is None else str(output_path)
        return {"rows_total": 3, "matched_rows": 1, "invalid_rows": 0, "results": []}

    monkeypatch.setattr(cli, "run_retrieval_query", _fake_run_retrieval_query)

    rc = cli._cmd_retrieval_query(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "idx.jsonl"),
                "out": str(tmp_path / "out.jsonl"),
                "normalized_title": "data_engineer",
                "role_family": None,
                "language_bucket": None,
                "location_type": None,
                "employment_type": None,
                "has_salary": "true",
                "has_skills": None,
                "title_is_other": None,
                "skills_contains": ["python"],
                "salary_currency": None,
                "sort_by": "published_at_desc",
                "limit": 10,
            },
        )
    )
    assert rc == 0
    assert called["input_path"] == str(tmp_path / "idx.jsonl")
    assert called["output_path"] == str(tmp_path / "out.jsonl")
    assert called["query"].normalized_title == "data_engineer"
    assert called["query"].has_salary is True


def test_cli_parser_retrieval_report_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["retrieval", "report", "--input", "data/jobs/jobs_indexed_en.jsonl", "--report-dir", "docs"])
    assert args.group == "retrieval"
    assert args.retrieval_cmd == "report"
