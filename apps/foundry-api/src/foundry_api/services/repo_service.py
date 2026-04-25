"""Repository query / mutation service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.enums import BranchState, FindingSeverity, PullRequestState
from foundry_core.models import (
    Branch,
    Finding,
    PullRequest,
    Repository,
)
from foundry_core.schemas import RepoSummary, RepositoryIn, RepositoryOut


async def list_repositories(session: AsyncSession) -> list[RepositoryOut]:
    result = await session.execute(select(Repository).order_by(Repository.created_at.desc()))
    return [RepositoryOut.model_validate(r) for r in result.scalars().all()]


async def get_repository(session: AsyncSession, repo_id: str) -> Repository | None:
    result = await session.execute(select(Repository).where(Repository.id == repo_id))
    return result.scalar_one_or_none()


async def create_repository(
    session: AsyncSession, payload: RepositoryIn
) -> RepositoryOut:
    repo = Repository(
        slug=payload.slug,
        name=payload.name,
        url=payload.url,
        default_branch=payload.default_branch,
        provider=payload.provider,
        local_path=payload.local_path,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(repo)
    await session.flush()
    return RepositoryOut.model_validate(repo)


async def summarize_repository(
    session: AsyncSession, repo: Repository
) -> RepoSummary:
    active = await session.scalar(
        select(func.count()).select_from(Branch).where(
            Branch.repository_id == repo.id, Branch.state == BranchState.ACTIVE
        )
    )
    stale = await session.scalar(
        select(func.count()).select_from(Branch).where(
            Branch.repository_id == repo.id,
            Branch.state.in_([BranchState.STALE, BranchState.ORPHANED]),
        )
    )
    open_prs = await session.scalar(
        select(func.count()).select_from(PullRequest).where(
            PullRequest.repository_id == repo.id,
            PullRequest.state == PullRequestState.OPEN,
        )
    )
    critical = await session.scalar(
        select(func.count()).select_from(Finding).where(
            Finding.repository_id == repo.id,
            Finding.severity.in_([FindingSeverity.HIGH, FindingSeverity.CRITICAL]),
        )
    )
    recent_merges = await session.scalar(
        select(func.count()).select_from(PullRequest).where(
            PullRequest.repository_id == repo.id,
            PullRequest.state == PullRequestState.MERGED,
        )
    )

    return RepoSummary(
        repository=RepositoryOut.model_validate(repo),
        active_branches=int(active or 0),
        stale_branches=int(stale or 0),
        open_prs=int(open_prs or 0),
        critical_findings=int(critical or 0),
        recent_merges=int(recent_merges or 0),
        last_synced_at=repo.last_synced_at,
    )
