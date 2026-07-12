from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .common import normalize_title, read_csv_dict, repo_root, write_json, write_jsonl


def _split_labels(raw: str) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in str(raw).split("\n") if x.strip()]


def build_esco_index(esco_dir: Path, out_jsonl: Path, out_meta: Path) -> dict:
    occupations_path = esco_dir / "occupations_en.csv"
    broader_path = esco_dir / "broaderRelationsOccPillar_en.csv"
    isco_path = esco_dir / "ISCOGroups_en.csv"
    occ_skill_path = esco_dir / "occupationSkillRelations_en.csv"

    occupations = read_csv_dict(occupations_path)
    broader = read_csv_dict(broader_path) if broader_path.exists() else []
    isco_groups = read_csv_dict(isco_path) if isco_path.exists() else []
    occ_skill = read_csv_dict(occ_skill_path) if occ_skill_path.exists() else []

    broader_map = {row.get("conceptUri", ""): row for row in broader}
    isco_map = {row.get("code", ""): row.get("preferredLabel", "") for row in isco_groups}

    top_skills: dict[str, list[str]] = defaultdict(list)
    skill_counter: dict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in occ_skill:
        occ_uri = row.get("occupationUri", "")
        skill = (row.get("skillLabel", "") or "").strip()
        if occ_uri and skill:
            skill_counter[occ_uri][skill] += 1
    for occ_uri, c in skill_counter.items():
        top_skills[occ_uri] = [k for k, _ in sorted(c.items(), key=lambda kv: kv[1], reverse=True)[:8]]

    rows = []
    for row in occupations:
        concept_uri = row.get("conceptUri", "")
        pref = (row.get("preferredLabel", "") or "").strip()
        if not pref:
            continue
        alt = _split_labels(row.get("altLabels", ""))
        hidden = _split_labels(row.get("hiddenLabels", ""))
        broader_row = broader_map.get(concept_uri, {})
        isco_code = (row.get("iscoGroup", "") or "").strip()
        rows.append(
            {
                "source": "esco",
                "concept_uri": concept_uri,
                "preferred_label": pref,
                "normalized_label": normalize_title(pref),
                "alt_labels": alt,
                "hidden_labels": hidden,
                "broader_label": broader_row.get("broaderLabel", "") or "",
                "broader_uri": broader_row.get("broaderUri", "") or "",
                "isco_group_code": isco_code,
                "isco_group_label": isco_map.get(isco_code, ""),
                "skills_preview": top_skills.get(concept_uri, []),
            }
        )

    write_jsonl(out_jsonl, rows)
    meta = {
        "occupations_rows": len(rows),
        "broader_rows": len(broader),
        "isco_rows": len(isco_groups),
        "occupation_skill_rows": len(occ_skill),
        "files": {
            "occupations_en": str(occupations_path),
            "broaderRelationsOccPillar_en": str(broader_path),
            "ISCOGroups_en": str(isco_path),
            "occupationSkillRelations_en": str(occ_skill_path),
        },
    }
    write_json(out_meta, meta)
    return meta


if __name__ == "__main__":
    root = repo_root()
    esco = root / "ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv"
    out_jsonl = root / "experiments/title_semantic_layer/reports/esco_index.jsonl"
    out_meta = root / "experiments/title_semantic_layer/reports/esco_index_meta.json"
    m = build_esco_index(esco, out_jsonl, out_meta)
    print(f"esco_index -> {out_jsonl} ({m['occupations_rows']} rows)")
