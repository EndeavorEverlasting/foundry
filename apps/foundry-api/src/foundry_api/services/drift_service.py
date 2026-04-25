"""Main-drift panel assembly."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.models import Branch
from foundry_core.schemas import BranchOut, DriftEntry, DriftPanel


async def build_drift_panel(session: AsyncSession, repo_id: str) -> DriftPanel:
    rs = await session.execute(
        select(Branch).where(Branch.repository_id == repo_id, ~Branch.is_default)
    )
    branches = list(rs.scalars().all())

    main_missing: list[DriftEntry] = []
    behind_main: list[DriftEntry] = []

    for b in branches:
        risk = _conflict_label(b.ahead_count, b.behind_count)
        entry = DriftEntry(
            branch=BranchOut.model_validate(b),
            ahead=b.ahead_count,
            behind=b.behind_count,
            conflict_risk=risk,
            readiness=b.readiness,
        )
        if b.ahead_count > 0:
            main_missing.append(entry)
        if b.behind_count > 0:
            behind_main.append(entry)

    main_missing.sort(key=lambda e: -e.ahead)
    behind_main.sort(key=lambda e: -e.behind)

    return DriftPanel(
        repository_id=repo_id,
        main_missing=main_missing,
        behind_main=behind_main,
    )


def _conflict_label(ahead: int, behind: int) -> str:
    if ahead == 0 or behind == 0:
        return "low"
    if ahead + behind >= 40:
        return "high"
    if ahead + behind >= 10:
        return "medium"
    return "low"
