from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from ddgs import DDGS


GREENHOUSE_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def _extract_slug(url: str) -> str | None:
    try:
        u = urlparse(url)
        host = (u.netloc or "").lower()
        parts = [p for p in (u.path or "").split("/") if p]
        if not parts:
            return None
        # ignore embed/app paths
        if parts[0].lower() in {"embed", "job_board", "job_app"}:
            return None
        slug = parts[0].lower()
        if host in GREENHOUSE_HOSTS:
            return slug
    except Exception:
        return None
    return None


def _is_bad_slug(slug: str) -> bool:
    s = slug.lower()
    return any(k in s for k in ["referral", "internal", "test"])


def _probe(slug: str) -> bool:
    url = GH_API.format(slug=slug)
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "jobintel/0.1"})
        if r.status_code != 200:
            print(f"Probe failed {slug}: {r.status_code}")
            return False
        data = r.json()
        print(f"Probe ok {slug}: {len(data.get('jobs', []))} jobs")
        return isinstance(data, dict) and "jobs" in data
    except Exception:
        print(f"Probe failed {slug}: exception")
        return False


def discover_from_ddg(queries: list[str], max_results: int = 50) -> list[str]:
    boards: list[str] = []
    seen = set()

    with DDGS() as ddgs:
        for q in queries:
            results = ddgs.text(q, max_results=max_results)
        for r in results:
            url = r.get("href") or r.get("url")
            if not isinstance(url, str):
                continue
            print(f"DDG hit: {url}")
            slug = _extract_slug(url)
            if not slug or slug in seen or _is_bad_slug(slug):
                continue
            seen.add(slug)
            if _probe(slug):
                boards.append(slug)
            time.sleep(0.3)
            time.sleep(1.0)

    return boards


def _load_existing(path: Path) -> list[str]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    boards = data.get("sources", {}).get("greenhouse", {}).get("boards", []) or []
    return [b for b in boards if isinstance(b, str)]


def write_targets(path: Path, boards: list[str]) -> None:
    existing = _load_existing(path)
    merged = list(dict.fromkeys(existing + boards))
    payload = {
        "sources": {
            "greenhouse": {"enabled": True, "boards": merged, "content": True},
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> None:
    queries = [
        "site:boards.greenhouse.io remote data",
        "site:boards.greenhouse.io Europe data",
        "site:boards.greenhouse.io EMEA data",
        "site:boards.greenhouse.io remote analytics",
        "site:boards.greenhouse.io data analyst",
        "site:boards.greenhouse.io Berlin data",
        "site:boards.greenhouse.io London data",
        "site:boards.greenhouse.io Amsterdam data",
        "site:boards.greenhouse.io distributed data",
        "site:boards.greenhouse.io SQL",
    ]

    boards = discover_from_ddg(queries, max_results=50)
    out = Path("config/generated/targets.yml")
    write_targets(out, boards)
    print(f"Wrote {out}")
    print(f"GH boards: {len(boards)}")


if __name__ == "__main__":
    main()
