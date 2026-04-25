"""Group stale branches into human-friendly buckets."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.enums import BranchState, StaleReason
from foundry_core.models import Branch
from foundry_core.schemas import BranchOut, StaleBranchBucket, StaleView


_BUCKETS = (
    (
        "forgotten",
        "Forgotten",
        "No recent commits; likely safe to archive or revisit.",
        {StaleReason.NO_RECENT_COMMITS},
    ),
    (
        "dormant-with-changes",
        "Dormant with changes",
        "Real commits waiting on a PR that never opened.",
        {StaleReason.NO_PR_ACTIVITY},
    ),
    (
        "orphaned-experiments",
        "Orphaned experiments",
        "No divergence from main and no activity — probably stale spikes.",
        {StaleReason.ORPHANED_FROM_MAIN},
    ),
    (
        "no-owner-activity",
        "No recent ownership activity",
        "Last author hasn't touched this area lately.",
        {StaleReason.NO_OWNER_ACTIVITY},
    ),
)


async def build_stale_view(session: AsyncSession, repo_id: str) -> StaleView:
    rs = await session.execute(
        select(Branch).where(
            Branch.repository_id == repo_id,
            Branch.state.in_([BranchState.STALE, BranchState.ORPHANED]),
        )
    )
    branches = list(rs.scalars().all())

    buckets: list[StaleBranchBucket] = []
    for slug, label, desc, match_reasons in _BUCKETS:
        _ = slug  # retained for future URLs, not emitted here
        bucket_branches = [
            BranchOut.model_validate(b)
            for b in branches
            if any(r in {r2 for r2 in b.stale_reasons or []} for r in (str(r.value) for r in match_reasons))
        ]
        if bucket_branches:
            buckets.append(
                StaleBranchBucket(label=label, description=desc, branches=bucket_branches)
            )

    return StaleView(repository_id=repo_id, buckets=buckets)
