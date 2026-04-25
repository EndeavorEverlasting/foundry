"""foundry-git: Git ingestion for Foundry services."""

from foundry_git.backend import (
    BranchRef,
    CommitInfo,
    DivergenceCounts,
    GitBackend,
    GitBackendError,
)
from foundry_git.gitpython_backend import GitPythonBackend
from foundry_git.service import RepoService

__all__ = [
    "BranchRef",
    "CommitInfo",
    "DivergenceCounts",
    "GitBackend",
    "GitBackendError",
    "GitPythonBackend",
    "RepoService",
]
