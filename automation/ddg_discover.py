from __future__ import annotations

import argparse
from urllib.parse import urlparse

import httpx

try:
    from ddgs import DDGS
except Exception as exc:  # pragma: no cover
    raise SystemExit("Install ddgs: uv pip install ddgs") from exc


GH_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
GH_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}


def _extract_slug(url: str) -> str | None:
    try:
        u = urlparse(url.strip())
        if u.netloc.lower() not in GH_HOSTS:
            return None
        parts = [p for p in u.path.split("/") if p]
        return parts[0].lower() if parts else None
    except Exception:
        return None


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
    ap = argparse.ArgumentParser(description="Discover Greenhouse boards via DuckDuckGo")
    ap.add_argument("--query", default="site:boards.greenhouse.io jobs")
    ap.add_argument("--max-results", type=int, default=50)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    slugs: set[str] = set()
    with DDGS() as ddgs:
        for item in ddgs.text(args.query, max_results=args.max_results):
            href = item.get("href") or item.get("url")
            if isinstance(href, str):
                slug = _extract_slug(href)
                if slug:
                    slugs.add(slug)

    for slug in sorted(slugs):
        if args.probe:
            print(f"{slug}\t{'ok' if _probe_slug(slug, args.timeout) else 'fail'}")
        else:
            print(slug)


if __name__ == "__main__":
    main()
