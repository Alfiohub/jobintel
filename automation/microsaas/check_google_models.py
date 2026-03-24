from __future__ import annotations

import argparse
import json
import os
from urllib import error as urlerror
from urllib import request as urlrequest


def main() -> None:
    ap = argparse.ArgumentParser(description="List available Google Gemini models for the provided API key.")
    ap.add_argument("--google-api-key", default=os.getenv("GOOGLE_API_KEY", ""))
    ap.add_argument("--google-url-base", default="https://generativelanguage.googleapis.com/v1beta")
    ap.add_argument("--timeout-sec", type=int, default=30)
    args = ap.parse_args()

    api_key = (args.google_api_key or "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY missing (set env or pass --google-api-key)")

    base = args.google_url_base.rstrip("/")
    url = f"{base}/models?key={api_key}"
    req = urlrequest.Request(url, method="GET")

    try:
        with urlrequest.urlopen(req, timeout=max(5, args.timeout_sec)) as resp:
            body = resp.read().decode("utf-8")
    except urlerror.HTTPError as e:
        details = ""
        try:
            details = e.read().decode("utf-8", errors="ignore")
        except Exception:
            details = str(e)
        raise RuntimeError(f"Google models list failed (url={url}): HTTP {e.code} {details}") from e

    obj = json.loads(body)
    models = obj.get("models", [])
    ids = [m.get("name", "") for m in models if isinstance(m, dict)]

    print(json.dumps({"count": len(ids), "models": ids, "raw": obj}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
