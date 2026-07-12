from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.product.alerts import cleanup_alert_runs


def _write_run(outdir: Path, run_id: str) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    obj = {
        "run_id": run_id,
        "run_timestamp": "2026-03-30T10:00:00+00:00",
        "searches_total": 1,
        "searches_enabled": 1,
        "searches_disabled": 0,
        "processed_ok": 1,
        "processed_error": 0,
        "total_new_matches": 1,
        "results": [],
    }
    (outdir / f"{run_id}.json").write_text(json.dumps(obj), encoding="utf-8")
    (outdir / f"{run_id}.md").write_text(f"# {run_id}\n", encoding="utf-8")


def test_cleanup_keep_last(tmp_path: Path) -> None:
    outdir = tmp_path / "alerts" / "runs"
    _write_run(outdir, "20260330T120003Z")
    _write_run(outdir, "20260330T120002Z")
    _write_run(outdir, "20260330T120001Z")

    rep = cleanup_alert_runs(runs_dir=outdir, keep_last=2)
    assert rep["keep_last"] == 2
    assert rep["removed_runs_count"] == 1
    assert (outdir / "20260330T120003Z.json").exists()
    assert (outdir / "20260330T120002Z.json").exists()
    assert not (outdir / "20260330T120001Z.json").exists()
