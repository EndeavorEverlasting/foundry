"""Branch drift math and conflict-risk heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class DriftResult:
    ahead: int
    behind: int
    diverged_at_sha: str | None
    main_file_overlap: int
    branch_files_touched: int

    @property
    def is_diverged(self) -> bool:
        return self.ahead > 0 and self.behind > 0


class ConflictRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def compute_conflict_risk(
    *, branch_files: set[str], main_files_since_fork: set[str]
) -> ConflictRisk:
    """Heuristic: overlap ratio between files touched in the branch and
    files changed on `main` since the merge base.

    Simple, explainable, good enough for v1. We'll upgrade to a file-range
    overlap analysis later.
    """

    if not branch_files or not main_files_since_fork:
        return ConflictRisk.NONE

    overlap = len(branch_files & main_files_since_fork)
    if overlap == 0:
        return ConflictRisk.NONE

    branch_ratio = overlap / len(branch_files)
    main_ratio = overlap / len(main_files_since_fork)
    ratio = max(branch_ratio, main_ratio)

    if ratio >= 0.5 or overlap >= 8:
        return ConflictRisk.HIGH
    if ratio >= 0.25 or overlap >= 4:
        return ConflictRisk.MEDIUM
    return ConflictRisk.LOW
