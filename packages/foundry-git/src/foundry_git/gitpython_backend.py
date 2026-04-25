"""GitPython implementation of GitBackend."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo
from git.objects.commit import Commit as GitCommit

from foundry_git.backend import (
    BranchRef,
    CommitInfo,
    DivergenceCounts,
    GitBackend,
    GitBackendError,
)


class GitPythonBackend(GitBackend):
    """GitBackend implementation backed by GitPython."""

    # --- clone / fetch ---------------------------------------------------

    def clone(self, url: str, dest: Path, *, depth: int | None = None) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if (dest / ".git").exists():
                return dest
            raise GitBackendError(f"destination exists and is not a git repo: {dest}")
        try:
            kwargs: dict[str, object] = {"no_single_branch": True}
            if depth is not None:
                kwargs["depth"] = depth
            Repo.clone_from(url, dest, **kwargs)
        except GitCommandError as exc:
            raise GitBackendError(f"clone failed for {url}: {exc}") from exc
        return dest

    def fetch(self, repo_path: Path) -> None:
        repo = self._repo(repo_path)
        try:
            for remote in repo.remotes:
                remote.fetch(prune=True, tags=True)
        except GitCommandError as exc:
            raise GitBackendError(f"fetch failed for {repo_path}: {exc}") from exc

    # --- introspection ---------------------------------------------------

    def list_branches(self, repo_path: Path) -> list[BranchRef]:
        repo = self._repo(repo_path)
        default = self.resolve_default_branch(repo_path)
        out: list[BranchRef] = []
        seen: set[str] = set()

        for head in repo.heads:
            out.append(
                BranchRef(
                    name=head.name,
                    head_sha=head.commit.hexsha,
                    is_default=head.name == default,
                    is_remote=False,
                )
            )
            seen.add(head.name)

        for remote in repo.remotes:
            for ref in remote.refs:
                short = ref.name.split("/", 1)[-1] if "/" in ref.name else ref.name
                if short == "HEAD":
                    continue
                if short in seen:
                    continue
                out.append(
                    BranchRef(
                        name=short,
                        head_sha=ref.commit.hexsha,
                        is_default=short == default,
                        is_remote=True,
                    )
                )
                seen.add(short)
        return out

    def resolve_default_branch(self, repo_path: Path, fallback: str = "main") -> str:
        repo = self._repo(repo_path)
        try:
            head_ref = repo.git.symbolic_ref("refs/remotes/origin/HEAD")
            return head_ref.rsplit("/", 1)[-1]
        except GitCommandError:
            pass
        for name in ("main", "master", "trunk", "develop"):
            try:
                repo.rev_parse(name)
                return name
            except (GitCommandError, ValueError, KeyError):
                continue
        if repo.heads:
            return repo.heads[0].name
        return fallback

    def head_sha(self, repo_path: Path, ref: str) -> str:
        repo = self._repo(repo_path)
        try:
            return repo.rev_parse(ref).hexsha
        except (GitCommandError, ValueError, KeyError) as exc:
            raise GitBackendError(f"ref not found: {ref}") from exc

    # --- commits ---------------------------------------------------------

    def iter_commits(
        self,
        repo_path: Path,
        ref: str,
        *,
        since_sha: str | None = None,
        limit: int | None = None,
        include_diffs: bool = True,
    ) -> Iterator[CommitInfo]:
        repo = self._repo(repo_path)
        rev = ref if since_sha is None else f"{since_sha}..{ref}"
        try:
            commits = repo.iter_commits(rev=rev, max_count=limit) if limit else repo.iter_commits(rev=rev)
        except GitCommandError as exc:
            raise GitBackendError(f"iter_commits failed for {ref}: {exc}") from exc

        for c in commits:
            yield _commit_to_info(c, include_diffs=include_diffs)

    # --- divergence ------------------------------------------------------

    def divergence(
        self, repo_path: Path, branch: str, base: str
    ) -> DivergenceCounts:
        repo = self._repo(repo_path)
        try:
            mb = self.merge_base(repo_path, branch, base)
            raw = repo.git.rev_list("--left-right", "--count", f"{base}...{branch}")
        except GitCommandError as exc:
            raise GitBackendError(
                f"divergence failed for {branch} vs {base}: {exc}"
            ) from exc

        behind_str, ahead_str = raw.split()
        return DivergenceCounts(
            ahead=int(ahead_str), behind=int(behind_str), merge_base=mb
        )

    def merge_base(self, repo_path: Path, a: str, b: str) -> str | None:
        repo = self._repo(repo_path)
        try:
            result = repo.git.merge_base(a, b)
            return result.strip() or None
        except GitCommandError:
            return None

    def files_changed_since(
        self, repo_path: Path, since_sha: str, until_sha: str
    ) -> list[str]:
        repo = self._repo(repo_path)
        try:
            out = repo.git.diff("--name-only", f"{since_sha}...{until_sha}")
        except GitCommandError as exc:
            raise GitBackendError(
                f"files_changed_since failed ({since_sha}->{until_sha}): {exc}"
            ) from exc
        return [line for line in out.splitlines() if line]

    # --- helpers ---------------------------------------------------------

    def _repo(self, repo_path: Path) -> Repo:
        try:
            return Repo(repo_path)
        except (InvalidGitRepositoryError, NoSuchPathError) as exc:
            raise GitBackendError(f"not a git repo: {repo_path}") from exc


def _commit_to_info(c: GitCommit, *, include_diffs: bool) -> CommitInfo:
    committed_at = datetime.fromtimestamp(c.committed_date, tz=timezone.utc)
    files_changed: list[str] = []
    additions = 0
    deletions = 0
    if include_diffs:
        stats = c.stats.files if c.parents else {}
        files_changed = list(stats.keys())
        for stat in stats.values():
            additions += int(stat.get("insertions", 0))
            deletions += int(stat.get("deletions", 0))

    return CommitInfo(
        sha=c.hexsha,
        short_sha=c.hexsha[:8],
        author_name=c.author.name or "",
        author_email=c.author.email or "",
        committed_at=committed_at,
        message=c.message.strip() if isinstance(c.message, str) else c.message.decode("utf-8", "replace").strip(),
        parents=[p.hexsha for p in c.parents],
        files_changed=files_changed,
        additions=additions,
        deletions=deletions,
    )
