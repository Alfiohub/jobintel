from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .interfaces import Collector, Logger, Notifier, Scorer, Store, null_logger


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    instant_threshold: int = 85
    digest_threshold: int = 70
    digest_max_items: int = 15


class Pipeline:

    def __init__(
        self,
        collectors: Sequence[Collector],
        scorer: Scorer,
        store: Store,
        notifier: Notifier,
        config: PipelineConfig = PipelineConfig(),
        logger: Logger | None = None,
    ):
        self.collectors = collectors
        self.scorer = scorer
        self.store = store
        self.notifier = notifier
        self.cfg = config
        self.log = logger or null_logger()

    def run_once(self) -> None:

        posts = []

        for c in self.collectors:
            try:
                self.log.info(f"Fetching from {c.name()}...")
                batch = c.fetch()
                self.log.info(f"{c.name()}: {len(batch)} posts")
                posts.extend(batch)

            except Exception as e:
                self.log.error(f"Collector {c.name()} failed: {e}")

        if not posts:
            self.log.info("No posts fetched.")
            return

        scored = self.scorer.score(posts)

        new_jobs = self.store.filter_new(scored)

        if not new_jobs:
            return

        instant = [j for j in new_jobs if j.score >= self.cfg.instant_threshold]
        digest = [j for j in new_jobs if self.cfg.digest_threshold <= j.score < self.cfg.instant_threshold]

        notified = []

        if instant:
            self.notifier.notify_instant(instant)
            notified.extend([j.fingerprint for j in instant])

        if digest:
            self.notifier.notify_digest(digest[: self.cfg.digest_max_items])
            notified.extend([j.fingerprint for j in digest[: self.cfg.digest_max_items]])

        self.store.mark_notified(notified)
