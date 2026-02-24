from __future__ import annotations

from pathlib import Path

from jobintel.canonical import CanonicalJob
from jobintel.model import ScoredJob
from jobintel.storage.sqlite_store import SQLiteStore


def _mk_scored(*, source: str, url: str, title: str, company: str, location: str, fp: str) -> ScoredJob:
    post = CanonicalJob.from_source(
        source=source,
        url=url,
        title=title,
        company_name=company,
        location_raw=location,
    )
    return ScoredJob(post=post, score=80, reasons=("test",), fingerprint=fp)


def test_idempotent_on_same_fingerprint(tmp_path: Path) -> None:
    db = tmp_path / "dedup.sqlite"
    store = SQLiteStore(str(db))

    j1 = _mk_scored(
        source="smartrecruiters",
        url="https://example.com/jobs/1",
        title="Data Engineer",
        company="Acme",
        location="Milan, IT",
        fp="fp-1",
    )

    first = store.filter_new([j1])
    second = store.filter_new([j1])

    assert len(first) == 1
    assert len(second) == 0


def test_secondary_dedup_on_title_company_location(tmp_path: Path) -> None:
    db = tmp_path / "dedup-secondary.sqlite"
    store = SQLiteStore(str(db))

    a = _mk_scored(
        source="smartrecruiters",
        url="https://careers.smartrecruiters.com/acme/1",
        title="Senior Data Engineer",
        company="Acme Corp",
        location="Rome, IT",
        fp="sr-fp-1",
    )
    b = _mk_scored(
        source="lever",
        url="https://jobs.lever.co/acme/xyz",
        title="Senior   Data Engineer",
        company="acme corp",
        location="Rome IT",
        fp="lever-fp-1",
    )

    first = store.filter_new([a])
    second = store.filter_new([b])

    assert len(first) == 1
    assert len(second) == 0
