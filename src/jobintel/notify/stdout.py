from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..interfaces import Notifier
from ..model import ScoredJob


def _fmt_job(j: ScoredJob) -> str:
    reasons = ", ".join(j.reasons) if j.reasons else "-"
    remote = "remote" if j.post.remote else "onsite/unknown"
    loc = j.post.location or "N/A"
    return (
        f"[{j.score:3d}] {j.post.title}\n"
        f"      {j.post.company} — {loc} — {remote}\n"
        f"      {j.post.url}\n"
        f"      reasons: {reasons}\n"
    )


@dataclass(frozen=True, slots=True)
class StdoutNotifier(Notifier):
    def notify_instant(self, jobs: Sequence[ScoredJob]) -> None:
        print("\n=== INSTANT (high match) ===")
        for j in jobs:
            print(_fmt_job(j))

    def notify_digest(self, jobs: Sequence[ScoredJob]) -> None:
        print("\n=== DIGEST (medium match) ===")
        for j in jobs:
            print(_fmt_job(j))
