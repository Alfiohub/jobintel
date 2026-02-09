from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Sequence

from .model import JobPost, ScoredJob


class Collector(ABC):

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def fetch(self) -> list[JobPost]:
        raise NotImplementedError


class Scorer(ABC):

    @abstractmethod
    def score(self, posts: Sequence[JobPost]) -> list[ScoredJob]:
        raise NotImplementedError


class Store(ABC):

    @abstractmethod
    def filter_new(self, jobs: Sequence[ScoredJob]) -> list[ScoredJob]:
        ...

    @abstractmethod
    def mark_notified(self, fingerprints: Sequence[str]) -> None:
        ...


class Notifier(ABC):

    @abstractmethod
    def notify_instant(self, jobs: Sequence[ScoredJob]) -> None: ...

    @abstractmethod
    def notify_digest(self, jobs: Sequence[ScoredJob]) -> None: ...


class Logger(Protocol):

    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...


def null_logger() -> Logger:
    class _Null:
        def info(self, msg: str) -> None: pass
        def warning(self, msg: str) -> None: pass
        def error(self, msg: str) -> None: pass

    return _Null()
