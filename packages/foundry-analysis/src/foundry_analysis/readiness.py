"""Compute a branch's aggregate merge-readiness state."""

from __future__ import annotations

from foundry_core.enums import ReadinessState


def compute_readiness(
    *,
    ahead: int,
    behind: int,
    has_open_pr: bool,
    is_draft_pr: bool,
    checks_passing: bool | None,
    has_reviewers: bool,
) -> ReadinessState:
    """Rules (first-match wins, most specific first):

    1. Failing checks on the PR -> FAILING_CHECKS
    2. PR is a draft -> DRAFT
    3. Behind main (needs rebase) -> NEEDS_REBASE
    4. Open PR with no reviewers assigned -> NEEDS_REVIEW
    5. Ahead with nothing wrong -> READY
    6. Default -> NEEDS_REVIEW
    """

    if has_open_pr and checks_passing is False:
        return ReadinessState.FAILING_CHECKS
    if has_open_pr and is_draft_pr:
        return ReadinessState.DRAFT
    if behind > 0 and ahead > 0:
        return ReadinessState.NEEDS_REBASE
    if has_open_pr and not has_reviewers:
        return ReadinessState.NEEDS_REVIEW
    if ahead > 0 and behind == 0:
        return ReadinessState.READY
    return ReadinessState.NEEDS_REVIEW
