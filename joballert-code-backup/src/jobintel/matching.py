from __future__ import annotations

from .model import JobPost


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def build_job_text(post: JobPost) -> str:
    return normalize_text(
        "\n".join(
            [
                post.title or "",
                post.company or "",
                post.location or "",
                post.description or "",
                " ".join(post.tags or ()),
                post.seniority or "",
                post.contract_type or "",
                post.salary_text or "",
            ]
        )
    )


def contains_term(text: str, term: str) -> bool:
    token = normalize_text(term)
    return bool(token) and token in text


def contains_any_term(text: str, terms: tuple[str, ...] | list[str]) -> bool:
    return any(contains_term(text, t) for t in terms)
