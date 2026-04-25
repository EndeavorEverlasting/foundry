"""Narrow Git backend interface.

Keeping this narrow means we can swap GitPython for pygit2 later without
touching any callers. All callers go through `GitBackend`.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable


class GitBackendError(RuntimeError):
    """Raised for any non-recoverable Git operation failure."""


@dataclass(frozen=True)
class BranchRef:
    name: str
    head_sha: str
    is_default: bool = False
    is_remote: bool = False


@dataclass(frozen=True)
class CommitInfo:
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    committed_at: datetime
    message: str
    parents: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0


@dataclass(frozen=True)
class DivergenceCounts:
    """Ahead/behind counts relative to a base ref."""

    ahead: int
    behind: int
    merge_base: str | None = None


@runtime_checkable
class GitBackend(Protocol):
    """Protocol implemented by concrete Git drivers."""

    def clone(self, url: str, dest: Path, *, depth: int | None = None) -> Path: ...

    def fetch(self, repo_path: Path) -> None: ...

    def list_branches(self, repo_path: Path) -> list[BranchRef]: ...

    def resolve_default_branch(self, repo_path: Path, fallback: str = "main") -> str: ...

    def head_sha(self, repo_path: Path, ref: str) -> str: ...

    def iter_commits(
        self,
        repo_path: Path,
        ref: str,
        *,
        since_sha: str | None = None,
        limit: int | None = None,
        include_diffs: bool = True,
    ) -> Iterator[CommitInfo]: ...

    def divergence(
        self, repo_path: Path, branch: str, base: str
    ) -> DivergenceCounts: ...

    def merge_base(self, repo_path: Path, a: str, b: str) -> str | None: ...

    def files_changed_since(
        self, repo_path: Path, since_sha: str, until_sha: str
    ) -> list[str]: ...

    def short_sha(self, sha: str, length: int = 8) -> str:
        return sha[:length]


def consume(it: Iterable[CommitInfo]) -> list[CommitInfo]:
    """Helper for small iterables, mostly useful in tests."""

    return list(it)
