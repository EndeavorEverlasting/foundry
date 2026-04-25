"""High-level ingestion service.

`RepoService` is what the worker calls. It owns the on-disk layout of
cloned repos and coordinates clone/fetch/list/iterate through the
`GitBackend`. It deliberately does no DB writes — the caller (worker)
handles persistence.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from foundry_git.backend import (
    BranchRef,
    CommitInfo,
    DivergenceCounts,
    GitBackend,
)

_SLUG_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def _stable_slug(url: str) -> str:
    parsed = urlparse(url)
    base = parsed.path or url
    base = base.strip("/").removesuffix(".git")
    base = _SLUG_RE.sub("-", base).strip("-") or "repo"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]  # noqa: S324
    return f"{base}-{digest}"


@dataclass(slots=True)
class EnsureResult:
    repo_path: Path
    slug: str
    was_cloned: bool


class RepoService:
    """Filesystem-aware façade over a `GitBackend`."""

    def __init__(self, backend: GitBackend, repos_dir: Path):
        self._backend = backend
        self._repos_dir = repos_dir
        self._repos_dir.mkdir(parents=True, exist_ok=True)

    # --- path layout -----------------------------------------------------

    @property
    def root(self) -> Path:
        return self._repos_dir

    def path_for(self, slug: str) -> Path:
        return self._repos_dir / slug

    @staticmethod
    def slug_for(url: str) -> str:
        return _stable_slug(url)

    # --- lifecycle -------------------------------------------------------

    def ensure(self, url: str, *, slug: str | None = None, local_path: Path | None = None) -> EnsureResult:
        """Ensure the repo exists on disk, cloning if needed.

        When `local_path` is provided we treat the repo as already on disk
        and skip cloning (useful for registering a dev repo like AxTask).
        """

        final_slug = slug or _stable_slug(url)

        if local_path is not None:
            if not (local_path / ".git").exists():
                raise FileNotFoundError(f"local_path is not a git repo: {local_path}")
            return EnsureResult(repo_path=local_path, slug=final_slug, was_cloned=False)

        dest = self.path_for(final_slug)
        was_cloned = not (dest / ".git").exists()
        self._backend.clone(url, dest)
        return EnsureResult(repo_path=dest, slug=final_slug, was_cloned=was_cloned)

    def sync(self, repo_path: Path) -> None:
        self._backend.fetch(repo_path)

    # --- delegations -----------------------------------------------------

    def list_branches(self, repo_path: Path) -> list[BranchRef]:
        return self._backend.list_branches(repo_path)

    def default_branch(self, repo_path: Path, fallback: str = "main") -> str:
        return self._backend.resolve_default_branch(repo_path, fallback=fallback)

    def divergence(self, repo_path: Path, branch: str, base: str) -> DivergenceCounts:
        return self._backend.divergence(repo_path, branch, base)

    def merge_base(self, repo_path: Path, a: str, b: str) -> str | None:
        return self._backend.merge_base(repo_path, a, b)

    def iter_commits(
        self,
        repo_path: Path,
        ref: str,
        *,
        since_sha: str | None = None,
        limit: int | None = None,
        include_diffs: bool = True,
    ) -> list[CommitInfo]:
        return list(
            self._backend.iter_commits(
                repo_path,
                ref,
                since_sha=since_sha,
                limit=limit,
                include_diffs=include_diffs,
            )
        )

    def files_changed_since(
        self, repo_path: Path, since_sha: str, until_sha: str
    ) -> list[str]:
        return self._backend.files_changed_since(repo_path, since_sha, until_sha)
