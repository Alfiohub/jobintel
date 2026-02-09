from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Sequence

from ..model import JobPost, ScoredJob
from ..config import ScoringConfig


def _fingerprint(p: JobPost) -> str:
    key = f"{p.source}|{p.company}|{p.url}".strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


@dataclass(frozen=True, slots=True)
class RuleBasedScorer:
    cfg: ScoringConfig

    def score(self, posts: Sequence[JobPost]) -> list[ScoredJob]:
        out: list[ScoredJob] = []
        for p in posts:
            out.append(self._score_one(p))
        return out

    def _score_one(self, p: JobPost) -> ScoredJob:
        text = "\n".join(
            [
                p.title or "",
                p.company or "",
                p.location or "",
                p.description or "",
                " ".join(p.tags or ()),
                p.seniority or "",
                p.contract_type or "",
                p.salary_text or "",
            ]
        )
        t = _norm(text)

        reasons: list[str] = []

        # Kill list
        for bad in self.cfg.exclude_keywords:
            b = _norm(bad)
            if b and b in t:
                return ScoredJob(
                    post=p,
                    score=0,
                    reasons=(f"kill:{b}",),
                    fingerprint=_fingerprint(p),
                )

        score = 50  # base

        # Role match
        role_hit = False
        for r in self.cfg.include_roles:
            rr = _norm(r)
            if rr and rr in t:
                role_hit = True
                break
        if role_hit:
            pts = int(self.cfg.weights.get("role_match", 20))
            score += pts
            reasons.append(f"role_match:+{pts}")

        # Skill weights (simple mapping; you can extend later)
        def skill_hit(skill: str) -> bool:
            s = _norm(skill)
            return bool(s) and (s in t)

        if skill_hit("sql"):
            pts = int(self.cfg.weights.get("skill_sql", 20))
            score += pts
            reasons.append(f"sql:+{pts}")

        if skill_hit("python"):
            pts = int(self.cfg.weights.get("skill_python", 10))
            score += pts
            reasons.append(f"python:+{pts}")

        if skill_hit("data quality") or skill_hit("testing") or skill_hit("dq"):
            pts = int(self.cfg.weights.get("skill_data_quality", 10))
            score += pts
            reasons.append(f"data_quality:+{pts}")

        # Generic include skills (small bump each, capped)
        bump = 0
        for s in self.cfg.include_skills:
            ss = _norm(s)
            if ss and ss not in ("sql", "python", "data quality", "testing", "dq") and ss in t:
                bump += 3
                reasons.append(f"{ss}:+3")
                if bump >= 12:
                    break
        score += bump

        # Remote boost
        if p.remote is True:
            pts = int(self.cfg.weights.get("remote", 15))
            score += pts
            reasons.append(f"remote:+{pts}")

        # Seniority penalty (very rough heuristic)
        senior_markers = ["principal", "staff", "head of", "director", "vp", "lead"]
        if any(m in t for m in senior_markers):
            pts = int(self.cfg.weights.get("senior_penalty", 25))
            score -= pts
            reasons.append(f"senior_penalty:-{pts}")

        score = max(0, min(100, score))

        return ScoredJob(
            post=p,
            score=score,
            reasons=tuple(reasons[:10]),
            fingerprint=_fingerprint(p),
        )
