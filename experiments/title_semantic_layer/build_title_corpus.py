from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from src.jobintel_next.pipelines.titles.rules import get_rules
from src.jobintel_next.pipelines.titles.taxonomy import get_default_taxonomy

from .common import normalize_title, read_jsonl, repo_root, write_json
from .taxonomy_overlay import get_semantic_taxonomy_overlay


def build_title_corpus(dataset_path: Path, output_path: Path, apply_overlay: bool = True) -> dict:
    taxonomy = get_default_taxonomy()
    rules = get_rules()
    overlay = get_semantic_taxonomy_overlay() if apply_overlay else {"existing_label_aliases": {}, "proposed_new_labels": []}

    rows = read_jsonl(dataset_path)

    samples_by_title: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        status = str(row.get("classification_status") or "").strip()
        normalized_title = str(row.get("normalized_title") or "").strip()
        title_raw = str(row.get("title_raw") or "").strip()
        if status == "matched" and normalized_title and title_raw:
            samples_by_title[normalized_title][title_raw] += 1

    rule_ids_by_title: dict[str, list[str]] = defaultdict(list)
    pattern_preview_by_title: dict[str, list[str]] = defaultdict(list)
    for rule in rules:
        rule_ids_by_title[rule.normalized_title].append(rule.rule_id)
        if len(pattern_preview_by_title[rule.normalized_title]) < 4:
            pattern_preview_by_title[rule.normalized_title].append(rule.pattern_text)

    canonical_entries = []
    existing_aliases = overlay.get("existing_label_aliases", {})
    for normalized_title in sorted(taxonomy.normalized_titles):
        role_family = taxonomy.role_family_for(normalized_title) or "other"
        sample_titles = [
            {"title": t, "count": c}
            for t, c in samples_by_title.get(normalized_title, Counter()).most_common(8)
        ]
        aliases = {normalize_title(normalized_title.replace("_", " "))}
        for item in sample_titles[:5]:
            aliases.add(normalize_title(item["title"]))
        for alias in existing_aliases.get(normalized_title, []):
            aliases.add(normalize_title(str(alias)))
        canonical_entries.append(
            {
                "normalized_title": normalized_title,
                "role_family": role_family,
                "aliases": sorted(a for a in aliases if a),
                "rule_ids": sorted(rule_ids_by_title.get(normalized_title, [])),
                "rule_patterns_preview": pattern_preview_by_title.get(normalized_title, []),
                "sample_titles": sample_titles,
                "corpus_source": "taxonomy",
            }
        )

    for proposed in overlay.get("proposed_new_labels", []):
        normalized_title = str(proposed.get("normalized_title") or "").strip()
        role_family = str(proposed.get("role_family") or "").strip()
        if not normalized_title or not role_family:
            continue
        aliases = {
            normalize_title(normalized_title.replace("_", " ")),
            *(normalize_title(str(alias)) for alias in proposed.get("aliases", [])),
        }
        canonical_entries.append(
            {
                "normalized_title": normalized_title,
                "role_family": role_family,
                "aliases": sorted(a for a in aliases if a),
                "rule_ids": [],
                "rule_patterns_preview": [],
                "sample_titles": [],
                "corpus_source": str(proposed.get("status") or "semantic_overlay"),
                "overlay_rationale": str(proposed.get("rationale") or ""),
            }
        )

    payload = {
        "source_dataset": str(dataset_path),
        "canonical_count": len(canonical_entries),
        "role_family_count": len(taxonomy.role_families),
        "canonical_entries": canonical_entries,
        "semantic_overlay": overlay,
    }
    write_json(output_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    dataset = root / "data/jobs/jobs_titled_en_recovery_v53_safe.jsonl"
    out = root / "experiments/title_semantic_layer/reports/internal_title_corpus.json"
    result = build_title_corpus(dataset, out, apply_overlay=True)
    print(f"internal_title_corpus -> {out} ({result['canonical_count']} canonical titles)")
