from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.titles.eval import run_title_eval


def test_run_title_eval_outputs_reports_and_clusters(tmp_path: Path) -> None:
    in_path = tmp_path / "jobs_titled_en.jsonl"
    rows = [
        {
            "url": "https://example.com/1",
            "title_clean": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "classification_status": "matched",
            "match_method": "rule_pattern",
            "confidence": 0.85,
        },
        {
            "url": "https://example.com/2",
            "title_clean": "Psychiatrist (MD)",
            "normalized_title": "other",
            "role_family": "other",
            "classification_status": "other",
            "match_method": "fallback",
            "confidence": 0.1,
            "notes": ["no_title_rule_match"],
        },
    ]
    with in_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    outdir = tmp_path / "docs"
    report = run_title_eval(input_path=in_path, outdir=outdir, sample_size=5, top_k=5)
    assert report["rows_total"] == 2
    assert (outdir / "title_eval_step13.json").exists()
    assert (outdir / "title_eval_step13.md").exists()
    assert (outdir / "title_other_clusters_step13.json").exists()
    assert (outdir / "sample_title_matched_step13.jsonl").exists()
    assert (outdir / "sample_title_other_step13.jsonl").exists()
    assert (outdir / "sample_title_non_role_step13.jsonl").exists()
