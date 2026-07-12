from __future__ import annotations

import argparse

from .config import load_config
from .pipeline import Pipeline
from .scoring.rule_based import RuleBasedScorer
from .storage.sqlite_store import SQLiteStore
from .notify.stdout import StdoutNotifier
from .source_registry import build_collectors_from_sources
from .enrichment import EnrichmentRules


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to YAML config")
    args = ap.parse_args()

    cfg = load_config(args.config)

    collectors = build_collectors_from_sources(cfg.sources_raw)

    scorer = RuleBasedScorer(cfg.scoring)
    enricher = EnrichmentRules(
        enabled=cfg.enrichment.enabled,
        min_quality_score=cfg.enrichment.min_quality_score,
    )
    store = SQLiteStore(cfg.storage.sqlite_path)
    notifier = StdoutNotifier()

    pipe = Pipeline(
        collectors=collectors,
        scorer=scorer,
        enricher=enricher,
        store=store,
        notifier=notifier,
        config=cfg.pipeline,
    )

    pipe.run_once()


if __name__ == "__main__":
    main()
