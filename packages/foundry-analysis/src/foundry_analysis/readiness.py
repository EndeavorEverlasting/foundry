"""Compute a branch's aggregate merge-readiness state."""

from __future__ import annotations

import re

from foundry_core.enums import ReadinessState

from foundry_analysis.capabilities import _glob_match


_HIGH_RISK_TAGS = frozenset({
    "engine_integration",
    "file_ingestion",
    "payroll_adjacent",
    "external_api",
    "merge_automation",
    "api_contract",
    "data_integrity",
    "policy_change",
    "branch_cleanup",
    "destructive_automation",
})


def compute_readiness(
    *,
    ahead: int,
    behind: int,
    has_open_pr: bool,
    is_draft_pr: bool,
    checks_passing: bool | None,
    has_reviewers: bool,
    is_stale: bool = False,
    branch_policy_violation: bool = False,
    docs_only: bool = False,
    risk_tags: list[str] | None = None,
) -> ReadinessState:
    """Rules (first-match wins, most specific first):

    1. Failing checks on the PR -> FAILING_CHECKS
    2. PR is a draft -> DRAFT
    3. Branch policy violation -> NEEDS_REVIEW (policy flag is external)
    4. Stale branch with changes -> AT_RISK
    5. Behind main (needs rebase) -> NEEDS_REBASE
    6. Open PR with no reviewers assigned -> NEEDS_REVIEW
    7. High-risk tags present -> MANUAL_REVIEW
    8. Docs-only changes -> SAFE_MERGE_CANDIDATE
    9. Ahead with nothing wrong -> READY
    10. Default -> NEEDS_REVIEW
    """

    if has_open_pr and checks_passing is False:
        return ReadinessState.FAILING_CHECKS
    if has_open_pr and is_draft_pr:
        return ReadinessState.DRAFT
    if is_stale and ahead > 0:
        return ReadinessState.AT_RISK
    if behind > 0 and ahead > 0:
        return ReadinessState.NEEDS_REBASE
    if risk_tags and any(t in _HIGH_RISK_TAGS for t in risk_tags):
        return ReadinessState.MANUAL_REVIEW
    if has_open_pr and not has_reviewers:
        return ReadinessState.NEEDS_REVIEW
    if docs_only and ahead > 0 and behind == 0:
        return ReadinessState.SAFE_MERGE_CANDIDATE
    if ahead > 0 and behind == 0:
        return ReadinessState.READY
    return ReadinessState.NEEDS_REVIEW


_BRANCH_POLICY_RE = re.compile(
    r"^(feature|feat|bugfix|hotfix|docs|spike|release)/\d{4}-\d{2}-\d{2}|"
    r"^(feature|feat|bugfix|hotfix|docs|spike|release)/.+"
)


def check_branch_name_policy(branch_name: str) -> str | None:
    """Return a policy-hold string if the branch name lacks expected context.

    Expected prefixes: feature/, feat/, bugfix/, hotfix/, docs/, spike/, release/
    or a date-stamped name (YYYY-MM-DD).
    """
    if _BRANCH_POLICY_RE.match(branch_name):
        return None
    if re.search(r"\d{4}-\d{2}-\d{2}", branch_name):
        return None
    return "hold:branch_policy_violation"


def is_safe_merge_candidate(
    *,
    files_changed: list[str],
    features: dict[str, list[str]],
) -> bool:
    """Check whether every changed file is documentation-only.

    Docs-only means the file ends with .md, lives under docs/, or matches
    the manifest's ``docs`` feature glob patterns.
    """
    if not files_changed:
        return False

    docs_patterns = features.get("docs", [])

    for f in files_changed:
        if f.endswith(".md"):
            continue
        if "/docs/" in f.replace("\\", "/"):
            continue
        if any(_glob_match(f, pat) for pat in docs_patterns):
            continue
        return False
    return True



