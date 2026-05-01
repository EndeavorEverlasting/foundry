"""Branch naming policy for Foundry-managed repositories.

Foundry-created branches must carry three pieces of operational context:

1. Work type, such as feature, fix, docs, chore, release, or hotfix.
2. Calendar date in ISO format: YYYY-MM-DD.
3. Searchable context slug describing the work.

Example:
    feature/2026-05-01-foundry-pr-cleanup-policy
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

BRANCH_NAME_PATTERN = re.compile(
    r"^(feature|fix|docs|chore|release|hotfix)/"
    r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$"
)

VALID_BRANCH_TYPES = frozenset({"feature", "fix", "docs", "chore", "release", "hotfix"})


@dataclass(frozen=True)
class BranchNameResult:
    """Structured result from a Foundry branch-name generation request."""

    branch_name: str
    branch_type: str
    branch_date: str
    context: str


def slugify_context(context: str) -> str:
    """Convert free-text branch context into a safe branch slug."""

    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", context.strip().lower())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    if not cleaned:
        raise ValueError("Branch context is required.")
    return cleaned


def build_branch_name(
    *,
    branch_type: str,
    context: str,
    branch_date: date | None = None,
) -> BranchNameResult:
    """Build a Foundry-compliant branch name from structured input."""

    if branch_type not in VALID_BRANCH_TYPES:
        raise ValueError(f"Invalid branch type: {branch_type}")

    resolved_date = branch_date or date.today()
    date_text = resolved_date.isoformat()
    context_slug = slugify_context(context)
    branch_name = f"{branch_type}/{date_text}-{context_slug}"

    if not validate_branch_name(branch_name):
        raise ValueError(f"Generated branch name violates Foundry policy: {branch_name}")

    return BranchNameResult(
        branch_name=branch_name,
        branch_type=branch_type,
        branch_date=date_text,
        context=context_slug,
    )


def validate_branch_name(branch_name: str) -> bool:
    """Return True when a branch name satisfies the Foundry date/context policy."""

    return bool(BRANCH_NAME_PATTERN.match(branch_name))
