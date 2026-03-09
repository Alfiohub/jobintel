from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


ALLOWED_EDUCATION = {"none", "high_school", "bachelor", "master", "phd", "unspecified"}


def _to_bool_01(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y"}:
        return "1"
    if s in {"0", "false", "no", "n"}:
        return "0"
    return ""


def _to_int_str(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        i = int(float(value))
    except Exception:
        return ""
    if i < 0 or i > 40:
        return ""
    return str(i)


def _extract_first_json_obj(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def _prompt_for_row(row: dict[str, str]) -> str:
    return (
        "You are labeling one job posting for a strict evaluation dataset.\n"
        "Return ONLY one JSON object with exactly these keys:\n"
        "gold_normalized_title, gold_role_family, gold_experience_years_min, gold_experience_years_max,\n"
        "gold_experience_required, gold_education_level, gold_degree_required, gold_soft_skills,\n"
        "confidence, needs_review, notes.\n"
        "Rules:\n"
        "- Use null when unknown.\n"
        "- experience fields must be numbers (0..40) or null.\n"
        "- education level must be one of: none, high_school, bachelor, master, phd, unspecified, or null.\n"
        "- gold_soft_skills should be semicolon-separated canonical labels or empty string.\n"
        "- needs_review must be true if confidence < 0.65 or if ambiguous.\n"
        "\n"
        f"title_raw: {row.get('title_raw','')}\n"
        f"title_clean: {row.get('title_clean','')}\n"
        f"description_clean_excerpt: {row.get('description_clean_excerpt','')}\n"
        f"pred_normalized_title: {row.get('pred_normalized_title','')}\n"
        f"pred_role_family: {row.get('pred_role_family','')}\n"
        f"pred_seniority: {row.get('pred_seniority','')}\n"
        f"pred_employment_type: {row.get('pred_employment_type','')}\n"
        f"pred_location_type: {row.get('pred_location_type','')}\n"
    )


def _call_ollama(prompt: str, *, model: str, url: str, timeout_sec: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }
    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")
    obj = json.loads(body)
    raw = obj.get("response", "")
    if not isinstance(raw, str):
        raise RuntimeError("Ollama response missing 'response' string")
    parsed = _extract_first_json_obj(raw)
    if not parsed:
        raise RuntimeError("Could not parse JSON object from Ollama response")
    return parsed


def _should_label(row: dict[str, str], *, overwrite: bool) -> bool:
    if overwrite:
        return True
    return not any(
        (row.get(k) or "").strip()
        for k in (
            "gold_normalized_title",
            "gold_role_family",
            "gold_experience_years_min",
            "gold_education_level",
        )
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Autolabel gold eval CSV via Ollama (Qwen).")
    ap.add_argument("--input", default="docs/gold_eval_set_v1.csv")
    ap.add_argument("--out", default="docs/gold_eval_set_v1_autolabeled.csv")
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    ap.add_argument("--timeout-sec", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0, help="0 means all rows.")
    ap.add_argument("--start", type=int, default=0, help="0-based row offset.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing gold_* fields.")
    ap.add_argument("--min-confidence", type=float, default=0.65)
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)
    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    labeled = 0
    errors = 0
    selected = rows[args.start :]
    if args.limit > 0:
        selected = selected[: args.limit]

    for row in selected:
        if not _should_label(row, overwrite=args.overwrite):
            continue
        try:
            out = _call_ollama(
                _prompt_for_row(row),
                model=args.model,
                url=args.ollama_url,
                timeout_sec=max(10, args.timeout_sec),
            )
            conf = out.get("confidence")
            try:
                conf_f = float(conf)
            except Exception:
                conf_f = 0.0
            needs_review = bool(out.get("needs_review")) or conf_f < args.min_confidence

            edu = out.get("gold_education_level")
            edu_s = (str(edu).strip().lower() if edu is not None else "")
            if edu_s and edu_s not in ALLOWED_EDUCATION:
                edu_s = "unspecified"

            exp_min = _to_int_str(out.get("gold_experience_years_min"))
            exp_max = _to_int_str(out.get("gold_experience_years_max"))
            if exp_min and exp_max and int(exp_min) > int(exp_max):
                exp_min, exp_max = exp_max, exp_min

            row["gold_normalized_title"] = str(out.get("gold_normalized_title") or "").strip()
            row["gold_role_family"] = str(out.get("gold_role_family") or "").strip()
            row["gold_experience_years_min"] = exp_min
            row["gold_experience_years_max"] = exp_max
            row["gold_experience_required"] = _to_bool_01(out.get("gold_experience_required"))
            row["gold_education_level"] = edu_s
            row["gold_degree_required"] = _to_bool_01(out.get("gold_degree_required"))
            row["gold_soft_skills"] = str(out.get("gold_soft_skills") or "").strip()
            row["review_status"] = "in_review" if needs_review else "approved"
            row["notes"] = str(out.get("notes") or "").strip()
            row["label_source"] = "ollama"
            row["label_model"] = args.model
            row["label_confidence"] = f"{conf_f:.3f}"
            row["needs_review"] = "1" if needs_review else "0"
            labeled += 1
        except (urlerror.URLError, urlerror.HTTPError, TimeoutError, RuntimeError, ValueError) as e:
            row["review_status"] = "todo"
            row["notes"] = f"autolabel_error: {e}"
            row["label_source"] = "ollama"
            row["label_model"] = args.model
            row["label_confidence"] = "0.000"
            row["needs_review"] = "1"
            errors += 1

    # Keep stable order + append extra metadata columns if missing.
    fieldnames = list(rows[0].keys())
    for extra in ("label_source", "label_model", "label_confidence", "needs_review"):
        if extra not in fieldnames:
            fieldnames.append(extra)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote: {out_path}")
    print(f"Rows total: {len(rows)} | attempted window: {len(selected)} | labeled: {labeled} | errors: {errors}")


if __name__ == "__main__":
    main()

