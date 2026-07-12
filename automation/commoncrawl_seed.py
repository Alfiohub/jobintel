from __future__ import annotations

import argparse
import json
from urllib.parse import urlparse

import httpx


CC_COLLINFO = "https://index.commoncrawl.org/collinfo.json"
GH_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def _resolve_latest_index(timeout_s: int = 20) -> str:
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(CC_COLLINFO)
        r.raise_for_status()
        data = r.json()
    if not isinstance(data, list) or not data:
        raise RuntimeError("collinfo unavailable")
    return str(data[0].get("id") or "").strip()


def _extract_slug(url: str) -> str | None:
    try:
        u = urlparse(url)
        if u.netloc.lower() not in GH_HOSTS:
            return None
        parts = [p for p in u.path.split("/") if p]
        return parts[0].lower() if parts else None
    except Exception:
        return None


def _query_cc(index_name: str, pattern: str, timeout_s: int = 30) -> list[str]:
    endpoint = f"https://index.commoncrawl.org/{index_name}-index"
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(endpoint, params={"url": pattern, "output": "json"})
        r.raise_for_status()
        lines = r.text.splitlines()
    out: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        u = obj.get("url")
        if isinstance(u, str):
            out.append(u)
    return out


def _probe_slug(slug: str, timeout_s: int) -> bool:
    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(GH_API.format(slug=slug))
            if r.status_code != 200:
                return False
            obj = r.json()
            return isinstance(obj, dict) and isinstance(obj.get("jobs"), list)
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Find Greenhouse board slugs from Common Crawl index")
    ap.add_argument("--index", default="latest", help="CC index, e.g. CC-MAIN-2026-10 or latest")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    index_name = _resolve_latest_index() if args.index.lower() == "latest" else args.index
    urls = _query_cc(index_name, "boards.greenhouse.io/*") + _query_cc(index_name, "job-boards.greenhouse.io/*")
    slugs = sorted({s for s in (_extract_slug(u) for u in urls) if s})

    for slug in slugs:
        if args.probe:
            print(f"{slug}\t{'ok' if _probe_slug(slug, args.timeout) else 'fail'}")
        else:
            print(slug)


if __name__ == "__main__":
    main()
