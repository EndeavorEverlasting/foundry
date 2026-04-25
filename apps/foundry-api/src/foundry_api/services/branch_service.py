"""Branch detail + evidence assembly."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.enums import BranchState, PullRequestState, ReadinessState
from foundry_core.evidence import EvidenceBundle
from foundry_core.models import Branch, Commit, PullRequest, Summary
from foundry_core.schemas import (
    BranchDetail,
    BranchOut,
    CommitOut,
    PullRequestOut,
    SummaryOut,
)


async def list_branches(
    session: AsyncSession,
    repo_id: str,
    *,
    state: BranchState | None = None,
    stale_only: bool = False,
    author: str | None = None,
    limit: int = 200,
) -> list[BranchOut]:
    stmt = select(Branch).where(Branch.repository_id == repo_id)
    if state is not None:
        stmt = stmt.where(Branch.state == state)
    if stale_only:
        stmt = stmt.where(Branch.state.in_([BranchState.STALE, BranchState.ORPHANED]))
    if author:
        stmt = stmt.where(Branch.last_author.ilike(f"%{author}%"))
    stmt = stmt.order_by(Branch.is_default.desc(), Branch.updated_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return [BranchOut.model_validate(b) for b in result.scalars().all()]


async def get_branch(session: AsyncSession, branch_id: str) -> Branch | None:
    result = await session.execute(select(Branch).where(Branch.id == branch_id))
    return result.scalar_one_or_none()


async def branch_detail(session: AsyncSession, branch: Branch) -> BranchDetail:
    commits_stmt = (
        select(Commit)
        .where(Commit.branch_id == branch.id)
        .order_by(Commit.committed_at.desc())
        .limit(50)
    )
    prs_stmt = (
        select(PullRequest)
        .where(PullRequest.branch_id == branch.id)
        .order_by(PullRequest.opened_at.desc().nullslast())
    )
    summary_stmt = (
        select(Summary)
        .where(Summary.branch_id == branch.id)
        .order_by(Summary.generated_at.desc())
        .limit(1)
    )

    commits_rs = await session.execute(commits_stmt)
    prs_rs = await session.execute(prs_stmt)
    summary_rs = await session.execute(summary_stmt)

    commits = [CommitOut.model_validate(c) for c in commits_rs.scalars().all()]
    prs = [PullRequestOut.model_validate(p) for p in prs_rs.scalars().all()]

    summary_row = summary_rs.scalar_one_or_none()
    latest_summary: SummaryOut | None = None
    if summary_row is not None:
        latest_summary = SummaryOut(
            id=summary_row.id,
            branch_id=summary_row.branch_id,
            headline=summary_row.headline,
            body=summary_row.body,
            confidence=summary_row.confidence,
            capabilities=list(summary_row.capabilities or []),
            evidence=EvidenceBundle.model_validate(summary_row.evidence or {}),
            generator=summary_row.generator,
            generated_at=summary_row.generated_at,
        )

    suggested = _suggest_actions(branch, prs)

    return BranchDetail(
        branch=BranchOut.model_validate(branch),
        commits=commits,
        latest_summary=latest_summary,
        pull_requests=prs,
        suggested_actions=suggested,
    )


def _suggest_actions(branch: Branch, prs: list[PullRequestOut]) -> list[str]:
    suggestions: list[str] = []
    has_open_pr = any(p.state == PullRequestState.OPEN for p in prs)

    if branch.readiness == ReadinessState.READY:
        suggestions.append("Merge this branch.")
    if branch.readiness == ReadinessState.NEEDS_REBASE:
        suggestions.append(f"Rebase onto the latest {branch.name} base.")
    if branch.readiness == ReadinessState.FAILING_CHECKS:
        suggestions.append("Fix failing CI checks.")
    if branch.readiness == ReadinessState.NEEDS_REVIEW and has_open_pr:
        suggestions.append("Request reviewers on the open PR.")
    if branch.state in (BranchState.STALE, BranchState.ORPHANED):
        suggestions.append("Close, archive, or reactivate this branch.")
    if not has_open_pr and branch.ahead_count > 0:
        suggestions.append("Open a pull request for review.")

    return suggestions
