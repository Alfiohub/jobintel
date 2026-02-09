from __future__ import annotations

import argparse

from .config import load_config
from .pipeline import Pipeline
from .collectors.greenhouse import GreenhouseBoard, GreenhouseCollector
from .scoring.rule_based import RuleBasedScorer
from .storage.sqlite_store import SQLiteStore
from .notify.stdout import StdoutNotifier


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to YAML config")
    args = ap.parse_args()

    cfg = load_config(args.config)

    collectors = []
    if cfg.greenhouse.enabled and cfg.greenhouse.boards:
        boards = [GreenhouseBoard(token=t, company_name=t) for t in cfg.greenhouse.boards]
        collectors.append(GreenhouseCollector(boards=boards, content=cfg.greenhouse.content))

    scorer = RuleBasedScorer(cfg.scoring)
    store = SQLiteStore(cfg.storage.sqlite_path)
    notifier = StdoutNotifier()

    pipe = Pipeline(
        collectors=collectors,
        scorer=scorer,
        store=store,
        notifier=notifier,
        config=cfg.pipeline,
    )

    pipe.run_once()


if __name__ == "__main__":
    main()
