from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load_rows(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if isinstance(obj, dict):
                out.append(obj)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate skills taxonomy on indexed dataset.")
    parser.add_argument("--indexed-jsonl", required=True, help="Path to jobs_indexed.jsonl")
    parser.add_argument("--out", required=True, help="Output markdown path")
    parser.add_argument("--top-n", type=int, default=40, help="Top skills to print")
    args = parser.parse_args()

    rows = _load_rows(Path(args.indexed_jsonl))
    if not rows:
        raise SystemExit("No rows found")

    total = len(rows)
    skills_counter: Counter[str] = Counter()
    rows_with_skills = 0
    total_skills = 0

    for r in rows:
        skills = r.get("skills") or []
        if isinstance(skills, list):
            clean = [str(x).strip() for x in skills if str(x).strip()]
        else:
            clean = []
        if clean:
            rows_with_skills += 1
        total_skills += len(clean)
        for s in clean:
            skills_counter[s] += 1

    unique_skills = len(skills_counter)
    avg_skills_all = round(total_skills / total, 3)
    avg_skills_nonempty = round(total_skills / rows_with_skills, 3) if rows_with_skills else 0.0
    top = skills_counter.most_common(max(1, args.top_n))

    report = Path(args.out)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# Skills Taxonomy Evaluation",
                "",
                f"- input: `{args.indexed_jsonl}`",
                f"- total rows: `{total}`",
                f"- rows with >=1 skill: `{rows_with_skills}` ({round(rows_with_skills*100.0/total,2)}%)",
                f"- total extracted skills: `{total_skills}`",
                f"- unique skills: `{unique_skills}`",
                f"- avg skills/row (all): `{avg_skills_all}`",
                f"- avg skills/row (rows with skills): `{avg_skills_nonempty}`",
                "",
                f"## Top {len(top)} Skills",
                "",
                "| skill | count | pct rows |",
                "|---|---:|---:|",
                *[
                    f"| {skill} | {cnt} | {round(cnt*100.0/total,2)}% |"
                    for skill, cnt in top
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote: {report}")
    print(f"unique_skills={unique_skills} avg_skills_all={avg_skills_all}")


if __name__ == "__main__":
    main()
